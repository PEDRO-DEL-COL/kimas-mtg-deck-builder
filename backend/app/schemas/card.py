from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    oracle_id: str
    name: str
    mana_cost: str | None = None
    type_line: str = ""
    oracle_text: str | None = None
    colors: list[str] = []
    color_identity: list[str] = []
    image_url: str | None = None


class CardPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oracle_id: str
    min_price_brl: Decimal | None = None
    avg_price_brl: Decimal | None = None
    ligamagic_url: str | None = None
    collected_at: datetime
