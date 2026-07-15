"""add public showcase access

Revision ID: 20260714_0005
Revises: 20260714_0004
Create Date: 2026-07-14
"""

import sqlalchemy as sa

from alembic import op

revision = "20260714_0005"
down_revision = "20260714_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vitrines",
        sa.Column("ativa", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column("itens_vitrine", sa.Column("token", sa.String(length=64), nullable=True))
    op.execute(
        "UPDATE itens_vitrine "
        "SET token = md5(random()::text || clock_timestamp()::text || id::text) "
        "WHERE token IS NULL"
    )
    op.alter_column("itens_vitrine", "token", nullable=False)
    op.create_index("ix_itens_vitrine_token", "itens_vitrine", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_itens_vitrine_token", table_name="itens_vitrine")
    op.drop_column("itens_vitrine", "token")
    op.drop_column("vitrines", "ativa")
