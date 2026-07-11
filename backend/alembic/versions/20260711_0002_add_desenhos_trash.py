"""add drawings trash

Revision ID: 20260711_0002
Revises: 20260710_0002
Create Date: 2026-07-11
"""

import sqlalchemy as sa

from alembic import op

revision = "20260711_0002"
down_revision = "20260710_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("desenhos", sa.Column("excluido_em", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_desenhos_excluido_em", "desenhos", ["excluido_em"])


def downgrade() -> None:
    op.drop_index("ix_desenhos_excluido_em", table_name="desenhos")
    op.drop_column("desenhos", "excluido_em")
