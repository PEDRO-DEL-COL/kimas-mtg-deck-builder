from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.card import Card

DASH = "—"
PRICES = {"c1": "0.25", "c2": "1.50", "c3": "1.50", "c7": "9999.99"}


def _card(
    cid: str,
    name: str,
    *,
    cmc: str = "0",
    type_line: str = "Instant",
    colors: str = "",
    identity: str | None = None,
    rarity: str = "common",
    legal: bool = True,
    text: str | None = None,
    pt: str | None = None,
) -> Card:
    ident = colors if identity is None else identity
    return Card(
        id=cid,
        oracle_id=f"o-{cid}",
        name=name,
        printed_name_pt=pt,
        mana_cost=None,
        cmc=Decimal(cmc),
        type_line=type_line,
        oracle_text=text,
        colors=list(colors),
        color_identity=list(ident),
        colors_key=colors,
        color_identity_key=ident,
        rarity=rarity,
        legal_commander=legal,
        image_url=f"https://img/{cid}.jpg",
        scryfall_uri=f"https://scryfall/{cid}",
    )


def make_seed() -> list[Card]:
    return [
        _card(
            "c1",
            "Lightning Bolt",
            cmc="1",
            colors="R",
            text="Deals 3 damage to any target.",
            pt="Raio",
        ),
        _card(
            "c2",
            "Counterspell",
            cmc="2",
            colors="U",
            text="Counter target spell.",
            rarity="uncommon",
        ),
        _card(
            "c3",
            "Sol Ring",
            cmc="1",
            type_line="Artifact",
            rarity="uncommon",
            text="{T}: Add {C}{C}.",
        ),
        _card("c4", "Command Tower", type_line="Land", text="Add one mana of any color."),
        _card(
            "c5",
            "Atraxa, Praetors' Voice",
            cmc="4",
            type_line=f"Legendary Creature {DASH} Phyrexian Angel Horror",
            colors="WUBG",
            rarity="mythic",
            text="Flying, vigilance, deathtouch, lifelink",
        ),
        _card(
            "c6",
            "Ragavan, Nimble Pilferer",
            cmc="1",
            type_line=f"Legendary Creature {DASH} Monkey Pirate",
            colors="R",
            rarity="mythic",
        ),
        _card("c7", "Black Lotus", cmc="0", type_line="Artifact", rarity="special", legal=False),
        _card(
            "c8",
            "Fire // Ice",
            cmc="4",
            colors="UR",
            rarity="uncommon",
            text="Gain 100% of the damage_dealt",
        ),
        _card("c9", "Wrath of God", cmc="4", type_line="Sorcery", colors="W", rarity="rare"),
        _card(
            "c10",
            "Dragon Artifact Golem",
            cmc="6.5",
            type_line=f"Artifact Creature {DASH} Golem",
            rarity="rare",
            identity="G",
        ),
    ]


@pytest.fixture
def db_client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as s:
        seed = make_seed()
        for c in seed:
            if c.id in PRICES:
                c.price_usd = Decimal(PRICES[c.id])
        seed[0].price_usd_foil = Decimal("1.10")
        seed[0].prices_updated_at = datetime(2024, 5, 6, 9, 3, tzinfo=UTC)
        s.add_all(seed)
        s.commit()

    def override() -> Iterator[Session]:
        with maker() as session:
            yield session

    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def ids(client: TestClient, **params: Any) -> list[str]:
    r = client.get("/api/cards", params=params)
    assert r.status_code == 200, r.text
    return [i["id"] for i in r.json()["items"]]


def test_list_all_default_sort_and_shape(db_client: TestClient) -> None:
    r = db_client.get("/api/cards")
    body = r.json()
    assert body["total"] == 10
    assert body["page"] == 1
    assert body["page_size"] == 24
    names = [i["name"] for i in body["items"]]
    assert names == sorted(names)
    first = body["items"][0]
    assert set(first) == {
        "id", "oracle_id", "name", "printed_name_pt", "mana_cost", "cmc", "type_line",
        "colors", "color_identity", "rarity", "legal_commander", "image_url",
        "price_usd", "price_usd_foil", "price_usd_etched", "prices_updated_at",
        "price_currency", "price_source",
    }  # fmt: skip
    assert isinstance(first["cmc"], float)


def test_q_name_and_portuguese(db_client: TestClient) -> None:
    assert ids(db_client, q="LIGHTNING") == ["c1"]
    assert ids(db_client, q="raio") == ["c1"]
    assert ids(db_client, q="zzz") == []


def test_identity_subset(db_client: TestClient) -> None:
    got = set(ids(db_client, identity="RU"))
    assert got == {"c1", "c2", "c3", "c4", "c6", "c7", "c8"}
    assert set(ids(db_client, identity="ru")) == got


def test_identity_colorless_only(db_client: TestClient) -> None:
    assert set(ids(db_client, identity="C")) == {"c3", "c4", "c7"}
    assert set(ids(db_client, identity="C", identity_mode="exact")) == {"c3", "c4", "c7"}


def test_identity_exact_and_superset(db_client: TestClient) -> None:
    assert ids(db_client, identity="UR", identity_mode="exact") == ["c8"]
    assert set(ids(db_client, identity="U", identity_mode="superset")) == {"c2", "c5", "c8"}
    assert set(ids(db_client, identity="WUBG", identity_mode="superset")) == {"c5"}


def test_colors_modes(db_client: TestClient) -> None:
    assert set(ids(db_client, colors="R", colors_mode="exact")) == {"c1", "c6"}
    assert set(ids(db_client, colors="R", colors_mode="superset")) == {"c1", "c6", "c8"}
    assert set(ids(db_client, colors="WU")) == {"c2", "c3", "c4", "c7", "c9", "c10"}
    # card identity of c10 is G but its colors are empty
    assert "c10" in ids(db_client, colors="C")


def test_type_and_subtype(db_client: TestClient) -> None:
    assert set(ids(db_client, type="legendary")) == {"c5", "c6"}
    assert set(ids(db_client, type="creature")) == {"c5", "c6", "c10"}
    assert ids(db_client, type="phyrexian") == []  # only in subtype
    assert ids(db_client, type="land") == ["c4"]
    assert ids(db_client, subtype="PIRATE") == ["c6"]
    assert ids(db_client, subtype="legendary") == []  # only in type part
    assert ids(db_client, subtype="golem", type="artifact") == ["c10"]


def test_cmc_range_and_sort(db_client: TestClient) -> None:
    assert set(ids(db_client, cmc_min=4, cmc_max=4)) == {"c5", "c8", "c9"}
    assert ids(db_client, cmc_min=6) == ["c10"]
    assert set(ids(db_client, cmc_max=0)) == {"c4", "c7"}
    order = ids(db_client, sort="cmc")
    assert order[:2] == ["c7", "c4"]  # cmc 0: Black Lotus, Command Tower (by name)
    assert order[-1] == "c10"


def test_text_with_wildcards_escaped(db_client: TestClient) -> None:
    assert ids(db_client, text="any target") == ["c1"]
    assert ids(db_client, text="100%") == ["c8"]
    assert ids(db_client, text="damage_dealt") == ["c8"]
    assert ids(db_client, text="damage_d_alt") == []
    assert ids(db_client, text="%") == ["c8"]


def test_rarity(db_client: TestClient) -> None:
    assert set(ids(db_client, rarity="mythic")) == {"c5", "c6"}
    assert set(ids(db_client, rarity="Rare, special")) == {"c7", "c9", "c10"}


def test_commander_legal(db_client: TestClient) -> None:
    assert ids(db_client, commander_legal="false") == ["c7"]
    assert len(ids(db_client, commander_legal="true")) == 9


def test_pagination(db_client: TestClient) -> None:
    r = db_client.get("/api/cards", params={"page_size": 4, "page": 3})
    body = r.json()
    assert body["total"] == 10
    assert body["page"] == 3
    assert body["page_size"] == 4
    assert len(body["items"]) == 2
    assert db_client.get("/api/cards", params={"page": 9}).json()["items"] == []


def test_combined_filters(db_client: TestClient) -> None:
    assert ids(db_client, identity="R", type="creature", rarity="mythic") == ["c6"]


@pytest.mark.parametrize(
    "params",
    [
        {"identity": "X"},
        {"identity": "CW"},
        {"colors": "WZ"},
        {"rarity": "legendary"},
        {"identity_mode": "bogus"},
        {"sort": "bogus"},
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"cmc_min": "abc"},
    ],
)
def test_validation_errors(db_client: TestClient, params: dict[str, Any]) -> None:
    assert db_client.get("/api/cards", params=params).status_code == 422


def test_card_detail(db_client: TestClient) -> None:
    r = db_client.get("/api/cards/c1")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Lightning Bolt"
    assert body["oracle_text"] == "Deals 3 damage to any target."
    assert body["scryfall_uri"] == "https://scryfall/c1"
    assert body["printed_name_pt"] == "Raio"


def test_card_not_found(db_client: TestClient) -> None:
    r = db_client.get("/api/cards/nope")
    assert r.status_code == 404
    assert r.json() == {"detail": "Card not found"}


def test_price_fields_in_summary_and_detail(db_client: TestClient) -> None:
    for body in (
        db_client.get("/api/cards", params={"q": "bolt"}).json()["items"][0],
        db_client.get("/api/cards/c1").json(),
    ):
        assert body["price_usd"] == "0.25"
        assert body["price_usd_foil"] == "1.10"
        assert body["price_usd_etched"] is None
        assert body["prices_updated_at"].startswith("2024-05-06T09:03")
        assert body["price_currency"] == "USD"
        assert body["price_source"] == "Scryfall"
    unpriced = db_client.get("/api/cards/c4").json()
    assert unpriced["price_usd"] is None and unpriced["prices_updated_at"] is None
    assert unpriced["price_currency"] == "USD" and unpriced["price_source"] == "Scryfall"


def test_price_filters_exclude_null_and_are_inclusive(db_client: TestClient) -> None:
    assert set(ids(db_client, price_min=0)) == {"c1", "c2", "c3", "c7"}
    assert set(ids(db_client, price_max=1.5)) == {"c1", "c2", "c3"}
    assert set(ids(db_client, price_min=1.5, price_max=1.5)) == {"c2", "c3"}
    assert ids(db_client, price_min=100) == ["c7"]
    assert ids(db_client, price_min=5000, price_max=6000) == []


def test_sort_by_price_nulls_last(db_client: TestClient) -> None:
    order = ids(db_client, sort="price")
    assert order[:4] == ["c1", "c2", "c3", "c7"]  # 0.25, 1.50 (Counterspell, Sol Ring), 9999.99
    rest = order[4:]
    assert len(rest) == 6
    assert ids(db_client, sort="price", price_min=1) == ["c2", "c3", "c7"]
