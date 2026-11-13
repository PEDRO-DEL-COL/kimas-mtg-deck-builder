from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (
        Index("ix_cards_name", "name"),
        Index("ix_cards_oracle_id", "oracle_id"),
        Index("ix_cards_cmc", "cmc"),
        Index("ix_cards_price_usd", "price_usd"),
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
    # Denormalised color keys in WUBRG order (e.g. "WUB", "" for colorless) so that color
    # filters work with plain string predicates on both SQLite and PostgreSQL.
    colors_key: Mapped[str] = mapped_column(String(5), default="")
    color_identity_key: Mapped[str] = mapped_column(String(5), default="")
    rarity: Mapped[str | None] = mapped_column(String(20))
    legal_commander: Mapped[bool] = mapped_column(default=False)
    image_url: Mapped[str | None] = mapped_column(String(500))
    scryfall_uri: Mapped[str | None] = mapped_column(String(500))
    # Scryfall USD prices; snapshot of the bulk file's `updated_at`.
    price_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_usd_foil: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_usd_etched: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    prices_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
