"""Card search query building (portable across SQLite and PostgreSQL)."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from sqlalchemy import ColumnElement, SQLColumnExpression, and_, func, not_, or_, select
from sqlalchemy.orm import Session

from app.models.card import Card

WUBRG = "WUBRG"
VALID_RARITIES = ("common", "uncommon", "rare", "mythic", "special", "bonus")
ColorMode = Literal["subset", "exact", "superset"]
SortKey = Literal["name", "cmc"]
DASH = "—"
_ESC = "\\"


class InvalidSearchError(ValueError):
    """Raised when a search parameter is syntactically invalid."""


@dataclass
class CardSearchParams:
    q: str | None = None
    identity: str | None = None
    identity_mode: ColorMode = "subset"
    colors: str | None = None
    colors_mode: ColorMode = "subset"
    type: str | None = None
    subtype: str | None = None
    cmc_min: float | None = None
    cmc_max: float | None = None
    text: str | None = None
    rarity: str | None = None
    commander_legal: bool | None = None
    sort: SortKey = "name"
    page: int = 1
    page_size: int = 24


def _escape(value: str) -> str:
    return value.replace(_ESC, _ESC + _ESC).replace("%", _ESC + "%").replace("_", _ESC + "_")


def _contains(
    column: SQLColumnExpression[str] | SQLColumnExpression[str | None], value: str
) -> ColumnElement[bool]:
    return func.lower(column).like(f"%{_escape(value.lower())}%", escape=_ESC)


def normalize_colors(value: str) -> str:
    """Return the WUBRG-ordered key for `value` ("" means colorless, given as "C")."""
    letters = set(value.upper())
    if not letters or not letters <= set(WUBRG + "C"):
        raise InvalidSearchError("Colors must be letters from WUBRG or C")
    if "C" in letters:
        if len(letters) > 1:
            raise InvalidSearchError("C (colorless) cannot be combined with other colors")
        return ""
    return "".join(c for c in WUBRG if c in letters)


def _color_filter(
    column: SQLColumnExpression[str], value: str, mode: ColorMode
) -> ColumnElement[bool]:
    key = normalize_colors(value)
    if mode == "exact" or (mode == "subset" and key == ""):
        return column == key
    if mode == "superset":
        # Colorless "superset" is every card.
        return and_(*[column.like(f"%{c}%") for c in key]) if key else column.is_not(None)
    return and_(*[not_(column.like(f"%{c}%")) for c in WUBRG if c not in key])


def parse_rarities(value: str) -> list[str]:
    items = [r.strip().lower() for r in value.split(",") if r.strip()]
    if not items or any(r not in VALID_RARITIES for r in items):
        raise InvalidSearchError(f"Rarity must be a comma-separated list of {VALID_RARITIES}")
    return items


def build_filters(p: CardSearchParams) -> list[ColumnElement[bool]]:
    conds: list[ColumnElement[bool]] = []
    if p.q:
        conds.append(or_(_contains(Card.name, p.q), _contains(Card.printed_name_pt, p.q)))
    if p.identity:
        conds.append(_color_filter(Card.color_identity_key, p.identity, p.identity_mode))
    if p.colors:
        conds.append(_color_filter(Card.colors_key, p.colors, p.colors_mode))
    # Type/subtype are split on the em dash using LIKE patterns only:
    #   type    -> "%t%-%" (t occurs before a dash) OR (no dash in line AND "%t%")
    #   subtype -> "%-%s%" (s occurs after a dash)
    # This is exact as long as the search term itself contains no em dash.
    if p.type:
        t = _escape(p.type.lower())
        line = func.lower(Card.type_line)
        conds.append(
            or_(
                line.like(f"%{t}%{DASH}%", escape=_ESC),
                and_(not_(line.like(f"%{DASH}%")), line.like(f"%{t}%", escape=_ESC)),
            )
        )
    if p.subtype:
        s = _escape(p.subtype.lower())
        conds.append(func.lower(Card.type_line).like(f"%{DASH}%{s}%", escape=_ESC))
    if p.cmc_min is not None:
        conds.append(Card.cmc >= Decimal(str(p.cmc_min)))
    if p.cmc_max is not None:
        conds.append(Card.cmc <= Decimal(str(p.cmc_max)))
    if p.text:
        conds.append(_contains(Card.oracle_text, p.text))
    if p.rarity:
        conds.append(Card.rarity.in_(parse_rarities(p.rarity)))
    if p.commander_legal is not None:
        conds.append(Card.legal_commander.is_(p.commander_legal))
    return conds


def search_cards(db: Session, p: CardSearchParams) -> tuple[list[Card], int]:
    conds = build_filters(p)
    total = db.scalar(select(func.count()).select_from(Card).where(*conds)) or 0
    stmt = select(Card).where(*conds)
    if p.sort == "cmc":
        stmt = stmt.order_by(Card.cmc, Card.name, Card.id)
    else:
        stmt = stmt.order_by(Card.name, Card.id)
    stmt = stmt.offset((p.page - 1) * p.page_size).limit(p.page_size)
    return list(db.scalars(stmt)), total
