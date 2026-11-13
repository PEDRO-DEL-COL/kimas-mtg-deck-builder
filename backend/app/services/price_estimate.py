"""Price conversion between currencies (interface only, no real implementation yet).

TODO: the BRL "estimativa" rule must be derived from a manual LigaMagic-vs-Scryfall
sample study (compare real LigaMagic BRL prices against Scryfall USD prices for a sample
of cards and fit a rule from that data).

NEVER convert with a flat USD -> BRL exchange rate: it does not reflect how the Brazilian
market prices cards.

No production converter is provided yet. ``IdentityConverter`` only handles
same-currency "conversions" and is mainly useful in tests.
"""

from typing import Protocol

from app.services.commander10 import Money


class PriceConverter(Protocol):
    def convert(self, money: Money, to_currency: str) -> Money | None:
        """Return `money` expressed in `to_currency`, or None if it cannot be converted."""
        ...


class IdentityConverter:
    """Converts only between identical currencies; anything else yields None."""

    def convert(self, money: Money, to_currency: str) -> Money | None:
        return money if money.currency == to_currency else None
