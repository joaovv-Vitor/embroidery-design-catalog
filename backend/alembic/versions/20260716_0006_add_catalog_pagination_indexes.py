"""add catalog pagination indexes

Revision ID: 20260716_0006
Revises: 20260714_0005
Create Date: 2026-07-16
"""

import sqlalchemy as sa

from alembic import op

revision = "20260716_0006"
down_revision = "20260714_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_desenhos_catalogo_criado_em_id",
        "desenhos",
        [sa.text("criado_em DESC"), sa.text("id DESC")],
        postgresql_where=sa.text("excluido_em IS NULL"),
    )
    op.create_index(
        "ix_desenhos_catalogo_categoria_criado_em_id",
        "desenhos",
        ["categoria_id", sa.text("criado_em DESC"), sa.text("id DESC")],
        postgresql_where=sa.text("excluido_em IS NULL"),
    )
    op.create_index(
        "ix_desenhos_catalogo_favoritos_criado_em_id",
        "desenhos",
        [sa.text("criado_em DESC"), sa.text("id DESC")],
        postgresql_where=sa.text("excluido_em IS NULL AND favorito IS TRUE"),
    )


def downgrade() -> None:
    op.drop_index("ix_desenhos_catalogo_favoritos_criado_em_id", table_name="desenhos")
    op.drop_index("ix_desenhos_catalogo_categoria_criado_em_id", table_name="desenhos")
    op.drop_index("ix_desenhos_catalogo_criado_em_id", table_name="desenhos")
