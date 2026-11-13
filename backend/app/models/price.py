from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class CardPrice(Base):
    __tablename__ = "card_prices"
    __table_args__ = (Index("ix_card_prices_oracle_id", "oracle_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    oracle_id: Mapped[str] = mapped_column(String(36))
    min_price_brl: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    avg_price_brl: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    ligamagic_url: Mapped[str | None] = mapped_column(String(500))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PriceRun(Base):
    __tablename__ = "price_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cards_ok: Mapped[int] = mapped_column(default=0)
    cards_failed: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")
