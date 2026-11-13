import gzip
import json
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.jobs import scryfall_import as imp
from app.models.card import Card

FIXTURE = Path(__file__).parent / "fixtures" / "scryfall" / "oracle_cards_sample.json"


@pytest.fixture
def cards() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data


@pytest.fixture
def session(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        yield s
    engine.dispose()


def test_streaming_parser_matches_json_load(cards: list[dict[str, Any]]) -> None:
    assert list(imp.iter_bulk_cards(FIXTURE, chunk_size=64)) == cards
    assert list(imp.iter_bulk_cards(FIXTURE)) == cards


def test_color_key_wubrg_order() -> None:
    assert imp.color_key(["G", "B"]) == "BG"
    assert imp.color_key(["R", "W", "U"]) == "WUR"
    assert imp.color_key([]) == ""


def test_card_to_row_normal_and_multicolor(cards: list[dict[str, Any]]) -> None:
    elves = imp.card_to_row(cards[0])
    assert elves is not None
    assert elves["name"] == "Llanowar Elves"
    assert elves["cmc"] == Decimal("1.0")
    assert elves["colors_key"] == "G"
    assert elves["legal_commander"] is True
    assert elves["printed_name_pt"] is None
    meren = imp.card_to_row(cards[1])
    assert meren is not None
    assert meren["color_identity_key"] == "BG"
    assert meren["color_identity"] == ["B", "G"]


def test_card_to_row_dfc(cards: list[dict[str, Any]]) -> None:
    row = imp.card_to_row(cards[2])
    assert row is not None
    assert row["image_url"].endswith("front/3/3/delver.jpg")
    assert row["mana_cost"] == "{U} // "
    assert row["oracle_text"].count("\n//\n") == 1
    assert row["colors"] == ["U"]
    assert row["colors_key"] == "U"


def test_card_to_row_split(cards: list[dict[str, Any]]) -> None:
    row = imp.card_to_row(cards[3])
    assert row is not None
    assert row["mana_cost"] == "{1}{R} // {1}{U}"
    assert row["colors_key"] == "UR" or row["colors_key"] == "UR"[::-1]
    assert "Tap target permanent." in row["oracle_text"]
    assert row["image_url"] is not None


def test_card_to_row_token_skipped_and_colorless(cards: list[dict[str, Any]]) -> None:
    assert imp.card_to_row(cards[4]) is None
    lotus = imp.card_to_row(cards[5])
    assert lotus is not None
    assert lotus["colors_key"] == ""
    assert lotus["color_identity_key"] == ""
    assert lotus["legal_commander"] is False


def test_reversible_card_uses_face_oracle_id() -> None:
    row = imp.card_to_row(
        {
            "id": "x",
            "layout": "reversible_card",
            "name": "R",
            "cmc": 0,
            "card_faces": [{"oracle_id": "o1", "oracle_text": "a"}],
        }
    )
    assert row is not None
    assert row["oracle_id"] == "o1"
    assert imp.card_to_row({"id": "y", "layout": "normal", "name": "N"}) is None


def test_import_inserts_then_updates(session: Session) -> None:
    stats = imp.import_file(session, FIXTURE, chunk_size=128)
    assert (stats.seen, stats.imported, stats.skipped) == (7, 6, 1)
    assert session.scalar(select(func.count()).select_from(Card)) == 6

    elves_id = "11111111-1111-1111-1111-111111111111"
    rows = [r for c in imp.iter_bulk_cards(FIXTURE) if (r := imp.card_to_row(c))]
    for r in rows:
        if r["id"] == elves_id:
            r["rarity"] = "rare"
    imp.upsert_cards(session, rows)
    session.expire_all()
    assert session.scalar(select(func.count()).select_from(Card)) == 6
    elves = session.get(Card, elves_id)
    assert elves is not None
    assert elves.rarity == "rare"
    meren = session.get(Card, "22222222-2222-2222-2222-222222222222")
    assert meren is not None
    assert "Naïve" in (meren.oracle_text or "")


def _bulk_transport(requests: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/bulk-data/oracle_cards":
            return httpx.Response(
                200,
                json={
                    "download_uri": "https://data.scryfall.io/oracle-cards/x.json",
                    "updated_at": "2024-05-06T09:03:07.123+00:00",
                },
            )
        return httpx.Response(200, content=FIXTURE.read_bytes())

    return httpx.MockTransport(handler)


def test_fetch_metadata_and_download(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    old = tmp_path / "oracle_cards-2024-01-01.json"
    old.write_text("[]")
    other = tmp_path / "default_cards-2024-01-01.json"
    other.write_text("[]")
    with httpx.Client(transport=_bulk_transport(requests)) as client:
        meta = imp.fetch_bulk_metadata(client, "oracle_cards")
        assert meta.updated_at.startswith("2024-05-06")
        assert "User-Agent" in requests[0].headers
        assert requests[0].headers["Accept"] == "application/json;q=0.9,*/*;q=0.8"
        path = imp.download_bulk_file(client, "oracle_cards", meta, tmp_path)
        assert path.name == "oracle_cards-2024-05-06.json"
        assert path.read_bytes() == FIXTURE.read_bytes()
        assert not old.exists()
        assert other.exists()
        assert not list(tmp_path.glob("*.part"))
        n = len(requests)
        imp.download_bulk_file(client, "oracle_cards", meta, tmp_path)
        assert len(requests) == n  # already downloaded: no new request


def _write_jsonl(path: Path, cards: list[dict[str, Any]], *, blank_lines: bool = True) -> Path:
    sep = "\n\n" if blank_lines else "\n"
    path.write_text(sep.join(json.dumps(c) for c in cards) + "\n", encoding="utf-8")
    return path


def test_jsonl_parser_matches_json_load(tmp_path: Path, cards: list[dict[str, Any]]) -> None:
    path = _write_jsonl(tmp_path / "oracle_cards-2024-05-06.jsonl", cards)
    assert list(imp.iter_bulk_cards(path)) == cards
    assert list(imp.iter_bulk_cards(path, chunk_size=16)) == cards
    padded = tmp_path / "padded.jsonl"
    padded.write_text("\n  \n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert list(imp.iter_bulk_cards(padded)) == cards


def _jsonl_transport(requests: list[httpx.Request], *, gz: bool = False) -> httpx.MockTransport:
    cards = json.loads(FIXTURE.read_text(encoding="utf-8"))
    body = ("\n".join(json.dumps(c) for c in cards) + "\n").encode()
    suffix = ".jsonl.gz" if gz else ".jsonl"
    payload = gzip.compress(body) if gz else body

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/bulk-data/oracle_cards":
            return httpx.Response(
                200,
                json={
                    "object": "bulk_data",
                    "jsonl_download_uri": f"https://data.scryfall.io/oracle-cards/x{suffix}",
                    "updated_at": "2024-05-06T09:03:07.123+00:00",
                },
            )
        return httpx.Response(200, content=payload)

    return httpx.MockTransport(handler)


@pytest.mark.parametrize("gz", [False, True])
def test_jsonl_metadata_and_download(tmp_path: Path, cards: list[dict[str, Any]], gz: bool) -> None:
    old = tmp_path / "oracle_cards-2024-01-01.json"
    old.write_text("[]")
    with httpx.Client(transport=_jsonl_transport([], gz=gz)) as client:
        meta = imp.fetch_bulk_metadata(client, "oracle_cards")
        assert meta.download_uri.endswith(".jsonl.gz" if gz else ".jsonl")
        path = imp.download_bulk_file(client, "oracle_cards", meta, tmp_path)
    assert path.name == "oracle_cards-2024-05-06.jsonl"
    assert not old.exists()
    assert list(imp.iter_bulk_cards(path)) == cards


def test_metadata_without_any_download_uri_fails() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"updated_at": "x"}))
    with httpx.Client(transport=transport) as client, pytest.raises(ValueError):
        imp.fetch_bulk_metadata(client, "oracle_cards")


def test_prices_mapped_to_decimal() -> None:
    card = {
        "id": "p1",
        "oracle_id": "o1",
        "layout": "normal",
        "name": "P",
        "cmc": 1,
        "prices": {"usd": "0.25", "usd_foil": None, "usd_etched": "3.10", "eur": "1.00"},
    }
    at = imp.parse_updated_at("2024-05-06T09:03:07.123+00:00")
    row = imp.card_to_row(card, at)
    assert row is not None
    assert row["price_usd"] == Decimal("0.25")
    assert row["price_usd_foil"] is None
    assert row["price_usd_etched"] == Decimal("3.10")
    assert row["prices_updated_at"] == at
    bare = imp.card_to_row({k: v for k, v in card.items() if k != "prices"})
    assert bare is not None
    assert bare["price_usd"] is None and bare["prices_updated_at"] is None


def test_updated_at_from_filename() -> None:
    got = imp.updated_at_from_filename(Path("data/oracle_cards-2024-05-06.jsonl"))
    assert got is not None and got.date().isoformat() == "2024-05-06"
    assert imp.updated_at_from_filename(Path("oracle_cards_sample.json")) is None


def test_import_persists_prices(session: Session, tmp_path: Path) -> None:
    card = {
        "id": "p1",
        "oracle_id": "o1",
        "layout": "normal",
        "name": "P",
        "cmc": 1,
        "prices": {"usd": "0.25", "usd_foil": "1.50", "usd_etched": None},
    }
    path = _write_jsonl(tmp_path / "oracle_cards-2024-05-06.jsonl", [card])
    at = imp.updated_at_from_filename(path)
    imp.import_file(session, path, prices_updated_at=at)
    got = session.get(Card, "p1")
    assert got is not None
    assert got.price_usd == Decimal("0.25") and got.price_usd_foil == Decimal("1.50")
    assert got.price_usd_etched is None
    assert got.prices_updated_at is not None and got.prices_updated_at.year == 2024
