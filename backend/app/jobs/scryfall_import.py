"""Scryfall Bulk Data importer.

Supports both JSON-array and JSON Lines bulk files (Scryfall now serves JSON Lines).

Downloads the bulk file (``oracle_cards`` by default), streams it without loading it
whole into memory, maps each card to a ``cards`` row and upserts it.

``oracle_cards`` (one printing per oracle_id) is recommended for card search. With
``default_cards`` there are many printings per oracle_id; they are all imported as-is
(keyed on the Scryfall printing id), with no extra de-duplication.

Only image URLs are stored; images are never hosted here.

Usage::

    python -m app.jobs.scryfall_import [--bulk-type oracle_cards|default_cards] [--file PATH]
"""

import argparse
import json
import logging
import re
import zlib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.card import Card

logger = logging.getLogger(__name__)

BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
BATCH_SIZE = 1000
CHUNK_SIZE = 1024 * 1024
WUBRG = "WUBRG"
GZIP_MAGIC = b"\x1f\x8b"
SKIPPED_LAYOUTS = frozenset(
    {
        "token",
        "double_faced_token",
        "emblem",
        "art_series",
        "vanguard",
        "scheme",
        "planar",
        "augment",
        "host",
    }
)

CardJson = dict[str, Any]
CardRow = dict[str, Any]


@dataclass
class ImportStats:
    seen: int = 0
    imported: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class BulkMetadata:
    download_uri: str
    updated_at: str

    @property
    def extension(self) -> str:
        """File extension for the saved file: JSON Lines or a JSON array."""
        path = self.download_uri.split("?", 1)[0]
        if path.endswith(".gz"):
            path = path[:-3]
        return ".jsonl" if path.endswith(".jsonl") else ".json"


def _headers() -> dict[str, str]:
    return {
        "User-Agent": get_settings().SCRYFALL_USER_AGENT,
        "Accept": "application/json;q=0.9,*/*;q=0.8",
    }


def fetch_bulk_metadata(client: httpx.Client, bulk_type: str) -> BulkMetadata:
    response = client.get(f"{BULK_DATA_URL}/{bulk_type}", headers=_headers())
    response.raise_for_status()
    data = response.json()
    # Scryfall now serves JSON Lines (`jsonl_download_uri`); keep the old key as a fallback.
    uri = data.get("jsonl_download_uri") or data.get("download_uri")
    if not uri:
        raise ValueError(f"Bulk data entry for {bulk_type!r} has no download URI")
    return BulkMetadata(download_uri=str(uri), updated_at=str(data["updated_at"]))


def download_bulk_file(
    client: httpx.Client,
    bulk_type: str,
    metadata: BulkMetadata,
    data_dir: Path | None = None,
) -> Path:
    """Download the bulk file unless today's version already exists; prune older files."""
    directory = data_dir if data_dir is not None else Path(get_settings().SCRYFALL_DATA_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{bulk_type}-{metadata.updated_at[:10]}{metadata.extension}"
    if target.exists():
        logger.info("Bulk file already present: %s", target)
    else:
        part = target.with_name(target.name + ".part")
        logger.info("Downloading %s to %s", metadata.download_uri, target)
        with client.stream("GET", metadata.download_uri, headers=_headers()) as response:
            response.raise_for_status()
            with part.open("wb") as fh:
                for chunk in _decoded_chunks(response, metadata.download_uri):
                    fh.write(chunk)
        part.replace(target)
    for pattern in (f"{bulk_type}-*.json", f"{bulk_type}-*.jsonl"):
        for old in directory.glob(pattern):
            if old.name < target.name:
                logger.info("Removing old bulk file %s", old)
                old.unlink()
    return target


def _decoded_chunks(response: httpx.Response, uri: str) -> Iterator[bytes]:
    """Yield body bytes; httpx already undoes Content-Encoding, a `.gz` URI is gunzipped here."""
    gunzip = uri.split("?", 1)[0].endswith(".gz")
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    first = True
    for chunk in response.iter_bytes(CHUNK_SIZE):
        if gunzip and first and not chunk.startswith(GZIP_MAGIC):
            gunzip = False  # already decoded by the transport
        first = False
        yield decompressor.decompress(chunk) if gunzip else chunk
    if gunzip:
        tail = decompressor.flush()
        if tail:
            yield tail


def iter_bulk_cards(path: Path, chunk_size: int = CHUNK_SIZE) -> Iterator[CardJson]:
    """Stream card objects from a bulk file: a JSON array or JSON Lines (auto-detected)."""
    with path.open("r", encoding="utf-8") as fh:
        head = ""
        while not head.strip():
            chunk = fh.read(chunk_size)
            if not chunk:
                return
            head += chunk
    if head.lstrip()[0] == "[":
        yield from _iter_json_array(path, chunk_size)
    else:
        yield from _iter_json_lines(path)


def _iter_json_lines(path: Path) -> Iterator[CardJson]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj


def _iter_json_array(path: Path, chunk_size: int) -> Iterator[CardJson]:
    """Stream the objects of a top-level JSON array without loading the whole file."""
    decoder = json.JSONDecoder()
    buffer = ""
    with path.open("r", encoding="utf-8") as fh:
        eof = False
        while not eof or buffer:
            if not eof:
                chunk = fh.read(chunk_size)
                if chunk:
                    buffer += chunk
                else:
                    eof = True
            pos = 0
            while True:
                while pos < len(buffer) and buffer[pos] in " \t\r\n,[]":
                    pos += 1
                if pos >= len(buffer):
                    break
                try:
                    obj, end = decoder.raw_decode(buffer, pos)
                except json.JSONDecodeError:
                    if eof:
                        raise
                    break  # object incomplete: need more data
                pos = end
                if isinstance(obj, dict):
                    yield obj
            buffer = buffer[pos:]
            if eof:
                break


def color_key(colors: Iterable[str]) -> str:
    present = set(colors)
    return "".join(c for c in WUBRG if c in present)


def _faces(card: CardJson) -> list[CardJson]:
    faces = card.get("card_faces")
    return [f for f in faces if isinstance(f, dict)] if isinstance(faces, list) else []


def _price(card: CardJson, key: str) -> Decimal | None:
    value = (card.get("prices") or {}).get(key)
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except ArithmeticError:
        return None


def parse_updated_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


_FILENAME_DATE = re.compile(r"-(\d{4}-\d{2}-\d{2})$")


def updated_at_from_filename(path: Path) -> datetime | None:
    """Derive the snapshot date from a ``<type>-<YYYY-MM-DD>`` file name, if possible."""
    match = _FILENAME_DATE.search(path.stem)
    return parse_updated_at(match.group(1)) if match else None


def card_to_row(card: CardJson, prices_updated_at: datetime | None = None) -> CardRow | None:
    if card.get("layout") in SKIPPED_LAYOUTS:
        return None
    faces = _faces(card)
    oracle_id = card.get("oracle_id") or (faces[0].get("oracle_id") if faces else None)
    if not oracle_id or not card.get("id"):
        return None

    mana_cost = card.get("mana_cost")
    if mana_cost is None and faces:
        mana_cost = " // ".join(str(f.get("mana_cost") or "") for f in faces)

    oracle_text = card.get("oracle_text")
    if oracle_text is None and faces:
        oracle_text = "\n//\n".join(str(f.get("oracle_text") or "") for f in faces)

    colors_raw = card.get("colors")
    if colors_raw is None:
        colors_raw = [c for f in faces for c in f.get("colors") or []]
    colors = [c for c in WUBRG if c in set(colors_raw)]
    identity = [c for c in WUBRG if c in set(card.get("color_identity") or [])]

    image_url: str | None = (card.get("image_uris") or {}).get("normal")
    if image_url is None and faces:
        image_url = (faces[0].get("image_uris") or {}).get("normal")

    legalities = card.get("legalities") or {}
    return {
        "id": card["id"],
        "oracle_id": oracle_id,
        "name": card.get("name", ""),
        # TODO: PT names need the all_cards bulk file filtered by lang=pt.
        "printed_name_pt": None,
        "mana_cost": mana_cost,
        "cmc": Decimal(str(card.get("cmc", 0))),
        "type_line": card.get("type_line") or "",
        "oracle_text": oracle_text,
        "colors": colors,
        "color_identity": identity,
        "colors_key": color_key(colors),
        "color_identity_key": color_key(identity),
        "rarity": card.get("rarity"),
        "legal_commander": legalities.get("commander") == "legal",
        "image_url": image_url,
        "scryfall_uri": card.get("scryfall_uri"),
        # TODO: oracle_cards picks one printing per card, so this price may not be the
        # cheapest printing; a later improvement is computing the minimum USD across all
        # printings from default_cards.
        "price_usd": _price(card, "usd"),
        "price_usd_foil": _price(card, "usd_foil"),
        "price_usd_etched": _price(card, "usd_etched"),
        "prices_updated_at": prices_updated_at,
    }


def upsert_cards(session: Session, rows: Iterable[CardRow]) -> int:
    """Upsert rows keyed on id in batches of 1000. Returns the number of rows written."""
    dialect = session.get_bind().dialect.name
    if dialect not in ("sqlite", "postgresql"):
        raise NotImplementedError(f"Unsupported database dialect: {dialect}")
    total = 0
    batch: list[CardRow] = []

    def flush() -> None:
        nonlocal total
        if not batch:
            return
        if dialect == "sqlite":
            sqlite_stmt = sqlite.insert(Card).values(batch)
            session.execute(
                sqlite_stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={c: sqlite_stmt.excluded[c] for c in batch[0] if c != "id"},
                )
            )
        else:
            pg_stmt = postgresql.insert(Card).values(batch)
            session.execute(
                pg_stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={c: pg_stmt.excluded[c] for c in batch[0] if c != "id"},
                )
            )
        total += len(batch)
        batch.clear()

    for row in rows:
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            flush()
    flush()
    session.commit()
    return total


def import_file(
    session: Session,
    path: Path,
    chunk_size: int = CHUNK_SIZE,
    prices_updated_at: datetime | None = None,
) -> ImportStats:
    stats = ImportStats()

    def rows() -> Iterator[CardRow]:
        for card in iter_bulk_cards(path, chunk_size):
            stats.seen += 1
            row = card_to_row(card, prices_updated_at)
            if row is None:
                stats.skipped += 1
                continue
            stats.imported += 1
            if stats.seen % 10000 == 0:
                logger.info("Processed %d cards", stats.seen)
            yield row

    upsert_cards(session, rows())
    logger.info(
        "Import done: seen=%d imported=%d skipped=%d", stats.seen, stats.imported, stats.skipped
    )
    return stats


def run_import(bulk_type: str | None = None, file: Path | None = None) -> ImportStats:
    prices_at: datetime | None = None
    if file is None:
        kind = bulk_type or get_settings().SCRYFALL_BULK_TYPE
        with httpx.Client(timeout=httpx.Timeout(60.0), follow_redirects=True) as client:
            metadata = fetch_bulk_metadata(client, kind)
            file = download_bulk_file(client, kind, metadata)
            prices_at = parse_updated_at(metadata.updated_at)
    else:
        prices_at = updated_at_from_filename(file)
    with SessionLocal() as session:
        return import_file(session, file, prices_updated_at=prices_at)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Import Scryfall bulk data into the database.")
    parser.add_argument("--bulk-type", choices=["oracle_cards", "default_cards"], default=None)
    parser.add_argument("--file", type=Path, default=None, help="Local file; skips download.")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    stats = run_import(bulk_type=args.bulk_type, file=args.file)
    logger.info("Finished at %s: %s", datetime.now(UTC).isoformat(), stats)


if __name__ == "__main__":
    main()
