"""Pure validation rules for the Commander 10 budget format (no DB access)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal

COMMANDER_PRICE_LIMIT = Decimal("5.00")
OTHERS_PRICE_LIMIT = Decimal("10.00")
DECK_SIZE = 100

BASIC_LAND_NAMES = frozenset(
    {
        "Plains",
        "Island",
        "Swamp",
        "Mountain",
        "Forest",
        "Wastes",
        "Snow-Covered Plains",
        "Snow-Covered Island",
        "Snow-Covered Swamp",
        "Snow-Covered Mountain",
        "Snow-Covered Forest",
        "Snow-Covered Wastes",
    }
)

ANY_NUMBER_PHRASE = "a deck can have any number of cards named"
UP_TO_SEVEN_PHRASE = "a deck can have up to seven cards named"


@dataclass(frozen=True)
class DeckEntry:
    name: str
    quantity: int
    price_brl: Decimal | None
    type_line: str = ""
    oracle_text: str = ""
    is_commander: bool = False


@dataclass(frozen=True)
class ValidationResult:
    total_cards: int
    card_count_ok: bool
    commander_count: int
    commander_price: Decimal | None
    commander_price_ok: bool
    others_total: Decimal
    others_total_ok: bool
    unknown_price_cards: list[str]
    singleton_violations: dict[str, int]
    budget_confirmed: bool
    is_valid: bool
    errors: list[str] = field(default_factory=list)


def is_basic_land(entry: DeckEntry) -> bool:
    return entry.name in BASIC_LAND_NAMES


def max_copies(entry: DeckEntry) -> int | None:
    """Return max allowed copies for a card, or None if unlimited."""
    if is_basic_land(entry):
        return None
    text = (entry.oracle_text or "").lower()
    if ANY_NUMBER_PHRASE in text:
        return None
    if UP_TO_SEVEN_PHRASE in text:
        return 7
    return 1


def validate_deck(entries: Sequence[DeckEntry]) -> ValidationResult:
    errors: list[str] = []
    total_cards = sum(e.quantity for e in entries)
    card_count_ok = total_cards == DECK_SIZE
    if not card_count_ok:
        errors.append(f"Deck has {total_cards} cards; exactly {DECK_SIZE} required.")

    # TODO: support Partner / Background (more than one commander).
    commanders = [e for e in entries if e.is_commander]
    commander_count = len(commanders)
    if commander_count != 1:
        errors.append(f"Exactly one commander required; found {commander_count}.")

    unknown: list[str] = []
    commander_price: Decimal | None = None
    commander_price_ok = False
    if commander_count == 1:
        commander = commanders[0]
        if commander.price_brl is None:
            unknown.append(commander.name)
        else:
            commander_price = commander.price_brl * commander.quantity
            commander_price_ok = commander_price <= COMMANDER_PRICE_LIMIT
            if not commander_price_ok:
                errors.append(f"Commander costs R$ {commander_price}; limit is R$ 5.00.")

    others_total = Decimal("0")
    for e in entries:
        if e.is_commander or is_basic_land(e):
            continue
        if e.price_brl is None:
            if e.name not in unknown:
                unknown.append(e.name)
        else:
            others_total += e.price_brl * e.quantity
    others_total_ok = others_total <= OTHERS_PRICE_LIMIT
    if not others_total_ok:
        errors.append(f"Other cards cost R$ {others_total}; limit is R$ 10.00.")

    counts: dict[str, int] = {}
    limits: dict[str, int | None] = {}
    for e in entries:
        counts[e.name] = counts.get(e.name, 0) + e.quantity
        limits[e.name] = max_copies(e)
    singleton_violations: dict[str, int] = {}
    for name, count in counts.items():
        limit = limits[name]
        if limit is not None and count > limit:
            singleton_violations[name] = count
            errors.append(f"{name}: {count} copies (max {limit}).")

    if unknown:
        errors.append("Unknown price: " + ", ".join(unknown))
    budget_confirmed = not unknown and commander_count == 1

    is_valid = (
        card_count_ok
        and commander_count == 1
        and commander_price_ok
        and others_total_ok
        and not singleton_violations
        and budget_confirmed
    )
    return ValidationResult(
        total_cards=total_cards,
        card_count_ok=card_count_ok,
        commander_count=commander_count,
        commander_price=commander_price,
        commander_price_ok=commander_price_ok,
        others_total=others_total,
        others_total_ok=others_total_ok,
        unknown_price_cards=unknown,
        singleton_violations=singleton_violations,
        budget_confirmed=budget_confirmed,
        is_valid=is_valid,
        errors=errors,
    )
