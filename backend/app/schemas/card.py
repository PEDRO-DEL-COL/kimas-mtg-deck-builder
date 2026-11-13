from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    oracle_id: str
    name: str
    printed_name_pt: str | None = None
    mana_cost: str | None = None
    cmc: float = 0.0
    type_line: str = ""
    colors: list[str] = []
    color_identity: list[str] = []
    rarity: str | None = None
    legal_commander: bool = False
    image_url: str | None = None


class CardDetail(CardSummary):
    oracle_text: str | None = None
    scryfall_uri: str | None = None


# Backwards-compatible alias.
CardRead = CardDetail


class CardPage(BaseModel):
    items: list[CardSummary]
    total: int
    page: int
    page_size: int


class CardPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oracle_id: str
    min_price_brl: Decimal | None = None
    avg_price_brl: Decimal | None = None
    ligamagic_url: str | None = None
    collected_at: datetime
