"""optional pg_trgm indexes for card text search (PostgreSQL only)

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-13 19:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INDEXES = {
    "ix_cards_name_trgm": "name",
    "ix_cards_oracle_text_trgm": "oracle_text",
    "ix_cards_type_line_trgm": "type_line",
}


def upgrade() -> None:
    # SQLite has no trigram support and simply falls back to plain LIKE scans.
    # get_context() (not get_bind()) so that offline `--sql` mode works too.
    if op.get_context().dialect.name != "postgresql":
        return
    # Keep the extension out of `public` (Supabase convention); the schema is
    # created when missing so this also works on plain Postgres.
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA extensions")
    for index, column in _INDEXES.items():
        op.execute(
            f"CREATE INDEX IF NOT EXISTS {index} ON cards "
            f"USING gin (lower({column}) extensions.gin_trgm_ops)"
        )


def downgrade() -> None:
    if op.get_context().dialect.name != "postgresql":
        return
    for index in _INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {index}")
