"""add catalog search indexes

Revision ID: 20260711_0003
Revises: 20260711_0002
Create Date: 2026-07-11
"""

from alembic import op

revision = "20260711_0003"
down_revision = "20260711_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        "ix_desenhos_nome_trgm",
        "desenhos",
        ["nome"],
        postgresql_using="gin",
        postgresql_ops={"nome": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_categorias_nome_trgm",
        "categorias",
        ["nome"],
        postgresql_using="gin",
        postgresql_ops={"nome": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_categorias_nome_trgm", table_name="categorias")
    op.drop_index("ix_desenhos_nome_trgm", table_name="desenhos")
