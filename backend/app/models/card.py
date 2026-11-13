from decimal import Decimal

from sqlalchemy import JSON, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (
        Index("ix_cards_name", "name"),
        Index("ix_cards_oracle_id", "oracle_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # scryfall_id
    oracle_id: Mapped[str] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(255))
    printed_name_pt: Mapped[str | None] = mapped_column(String(255))
    mana_cost: Mapped[str | None] = mapped_column(String(100))
    cmc: Mapped[Decimal] = mapped_column(Numeric(6, 1), default=Decimal("0"))
    type_line: Mapped[str] = mapped_column(String(255), default="")
    oracle_text: Mapped[str | None] = mapped_column(Text)
    colors: Mapped[list[str]] = mapped_column(JSON, default=list)
    color_identity: Mapped[list[str]] = mapped_column(JSON, default=list)
    rarity: Mapped[str | None] = mapped_column(String(20))
    legal_commander: Mapped[bool] = mapped_column(default=False)
    image_url: Mapped[str | None] = mapped_column(String(500))
    scryfall_uri: Mapped[str | None] = mapped_column(String(500))
