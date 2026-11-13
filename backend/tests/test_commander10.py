from decimal import Decimal

from app.services.commander10 import DeckEntry, Money, ValidationResult, validate_deck
from app.services.price_estimate import IdentityConverter

D = Decimal


def brl(value: str) -> Money:
    return Money(D(value), "BRL")


def usd(value: str) -> Money:
    return Money(D(value), "USD")


class FakeUsdToBrl:
    """Test-only converter with an arbitrary fixed factor (not a real rule)."""

    def convert(self, money: Money, to_currency: str) -> Money | None:
        if money.currency == to_currency:
            return money
        if (money.currency, to_currency) == ("USD", "BRL"):
            return Money(money.amount * 2, "BRL")
        return None


ANY_TEXT = "A deck can have any number of cards named {}."
SEVEN_TEXT = "A deck can have up to seven cards named {}."


def cmd(price: str | None = "5.00", name: str = "Boss") -> DeckEntry:
    return DeckEntry(
        name, 1, None if price is None else brl(price), "Legendary Creature", "", is_commander=True
    )


def build(
    commander: DeckEntry | None = None,
    *,
    nonbasic_count: int = 50,
    price: str | None = "0.20",
    extra: list[DeckEntry] | None = None,
    fill_basics: bool = True,
) -> list[DeckEntry]:
    unit = None if price is None else brl(price)
    entries: list[DeckEntry] = [commander] if commander is not None else []
    entries += [DeckEntry(f"Card {i}", 1, unit) for i in range(nonbasic_count)]
    entries += extra or []
    if fill_basics:
        missing = 100 - sum(e.quantity for e in entries)
        if missing > 0:
            entries.append(DeckEntry("Forest", missing, brl("0.50"), "Basic Land - Forest"))
    return entries


def test_valid_deck() -> None:
    r = validate_deck(build(cmd("4.99")))
    assert r.is_valid and r.budget_confirmed
    assert r.total_cards == 100
    assert r.others_total == D("10.00")
    assert r.errors == []


def test_commander_price_exceeded() -> None:
    r = validate_deck(build(cmd("5.01")))
    assert not r.commander_price_ok and not r.is_valid


def test_boundaries_pass() -> None:
    r = validate_deck(build(cmd("5.00")))
    assert r.commander_price_ok and r.others_total_ok and r.is_valid


def test_others_total_exceeded() -> None:
    r = validate_deck(build(cmd(), price="0.21"))
    assert r.others_total == D("10.50")
    assert not r.others_total_ok and not r.is_valid


def test_quantity_multiplies_price() -> None:
    extra = [DeckEntry("Rats", 2, brl("3.00"), oracle_text=ANY_TEXT.format("Rats"))]
    r = validate_deck(build(cmd(), nonbasic_count=50, price="0.00", extra=extra))
    assert r.others_total == D("6.00")


def test_basic_lands_excluded_from_total_and_singleton() -> None:
    extra = [
        DeckEntry("Island", 20, brl("99.00"), "Basic Land - Island"),
        DeckEntry("Snow-Covered Swamp", 10, brl("99.00"), "Basic Snow Land - Swamp"),
    ]
    r = validate_deck(build(cmd(), nonbasic_count=40, price="0.10", extra=extra))
    assert r.others_total == D("4.00")
    assert r.singleton_violations == {}
    assert r.is_valid


def test_basic_land_unknown_price_ignored() -> None:
    extra = [DeckEntry("Mountain", 10, None, "Basic Land - Mountain")]
    r = validate_deck(build(cmd(), nonbasic_count=49, price="0.10", extra=extra))
    assert r.unknown_price_cards == []


def test_singleton_violation() -> None:
    extra = [DeckEntry("Sol Ring", 2, brl("1.00"))]
    r = validate_deck(build(cmd(), nonbasic_count=48, price="0.10", extra=extra))
    assert r.singleton_violations == {"Sol Ring": 2}
    assert not r.is_valid


def test_any_number_card_allowed() -> None:
    text = ANY_TEXT.format("Persistent Petitioners")
    extra = [DeckEntry("Persistent Petitioners", 30, brl("0.10"), oracle_text=text)]
    r = validate_deck(build(cmd(), nonbasic_count=20, price="0.01", extra=extra))
    assert r.singleton_violations == {}
    assert r.is_valid


def test_seven_dwarves_limit() -> None:
    text = SEVEN_TEXT.format("Seven Dwarves")
    ok_extra = [DeckEntry("Seven Dwarves", 7, brl("0.10"), oracle_text=text)]
    ok = validate_deck(build(cmd(), nonbasic_count=40, price="0.01", extra=ok_extra))
    assert ok.singleton_violations == {} and ok.is_valid
    bad_extra = [DeckEntry("Seven Dwarves", 8, brl("0.10"), oracle_text=text)]
    bad = validate_deck(build(cmd(), nonbasic_count=40, price="0.01", extra=bad_extra))
    assert bad.singleton_violations == {"Seven Dwarves": 8}
    assert not bad.is_valid


def test_wrong_card_count() -> None:
    r = validate_deck(build(cmd(), fill_basics=False))
    assert r.total_cards == 51
    assert not r.card_count_ok and not r.is_valid
    r2 = validate_deck(build(cmd(), nonbasic_count=50, extra=[DeckEntry("Forest", 60, None)]))
    assert r2.total_cards == 111 and not r2.card_count_ok


def test_unknown_prices_reported() -> None:
    entries = build(cmd(), extra=[DeckEntry("Mystery", 1, None)], nonbasic_count=49)
    r = validate_deck(entries)
    assert r.unknown_price_cards == ["Mystery"]
    assert not r.budget_confirmed and not r.is_valid


def test_unknown_commander_price() -> None:
    r = validate_deck(build(cmd(None)))
    assert r.unknown_price_cards == ["Boss"]
    assert r.commander_price is None and not r.commander_price_ok
    assert not r.budget_confirmed and not r.is_valid


def test_missing_commander() -> None:
    r = validate_deck(build(None))
    assert r.commander_count == 0 and not r.is_valid
    assert any("commander" in e.lower() for e in r.errors)


def test_multiple_commanders() -> None:
    r = validate_deck(build(cmd(), extra=[cmd("1.00", "Second")], nonbasic_count=49))
    assert r.commander_count == 2 and not r.is_valid


def test_result_is_frozen() -> None:
    r: ValidationResult = validate_deck(build(cmd()))
    try:
        r.is_valid = False  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("expected frozen dataclass")


def usd_deck(commander_price: str, price: str) -> list[DeckEntry]:
    entries = [DeckEntry("Boss", 1, usd(commander_price), "Legendary Creature", "", True)]
    entries += [DeckEntry(f"Card {i}", 1, usd(price)) for i in range(50)]
    entries.append(DeckEntry("Forest", 49, None, "Basic Land - Forest"))
    return entries


def test_usd_entries_vs_brl_limits_not_evaluable() -> None:
    r = validate_deck(usd_deck("1.00", "0.10"))
    assert r.budget_currency_mismatch
    assert not r.budget_confirmed and not r.is_valid
    assert r.commander_price is None and not r.commander_price_ok
    assert not r.others_total_ok
    assert any("cannot be evaluated" in e for e in r.errors)


def test_brl_entries_have_no_mismatch() -> None:
    r = validate_deck(build(cmd("5.00")))
    assert not r.budget_currency_mismatch and r.budget_confirmed


def test_identity_converter_does_not_convert_usd() -> None:
    r = validate_deck(usd_deck("1.00", "0.10"), IdentityConverter())
    assert r.budget_currency_mismatch and not r.is_valid


def test_converter_makes_usd_deck_evaluable() -> None:
    ok = validate_deck(usd_deck("2.50", "0.10"), FakeUsdToBrl())  # 5.00 BRL / 10.00 BRL
    assert not ok.budget_currency_mismatch
    assert ok.commander_price == D("5.00") and ok.others_total == D("10.00")
    assert ok.is_valid
    bad = validate_deck(usd_deck("2.51", "0.10"), FakeUsdToBrl())
    assert not bad.commander_price_ok and not bad.is_valid and not bad.budget_currency_mismatch
