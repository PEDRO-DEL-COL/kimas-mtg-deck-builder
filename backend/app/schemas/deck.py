from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeckCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oracle_id: str
    quantity: int
    category: str | None = None


class DeckCreate(BaseModel):
    name: str
    format: str = "commander10"
    commander_oracle_id: str | None = None


class DeckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    format: str
    commander_oracle_id: str | None = None
    created_at: datetime
    updated_at: datetime
