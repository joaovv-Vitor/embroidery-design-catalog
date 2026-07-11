"""add relationship indexes

Revision ID: 20260710_0002
Revises: 20260710_0001
Create Date: 2026-07-10
"""

from alembic import op

revision = "20260710_0002"
down_revision = "20260710_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_desenhos_categoria_id", "desenhos", ["categoria_id"])
    op.create_index("ix_matrizes_origem_importacao_id", "matrizes", ["origem_importacao_id"])
    op.create_index("ix_itens_importacao_importacao_id", "itens_importacao", ["importacao_id"])


def downgrade() -> None:
    op.drop_index("ix_itens_importacao_importacao_id", table_name="itens_importacao")
    op.drop_index("ix_matrizes_origem_importacao_id", table_name="matrizes")
    op.drop_index("ix_desenhos_categoria_id", table_name="desenhos")
