"""create showcase tables

Revision ID: 20260714_0004
Revises: 20260711_0003
Create Date: 2026-07-14
"""

import sqlalchemy as sa

from alembic import op

revision = "20260714_0004"
down_revision = "20260711_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vitrines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("nome_cliente", sa.String(length=255), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vitrines_token", "vitrines", ["token"], unique=True)
    op.create_index("ix_vitrines_expira_em", "vitrines", ["expira_em"])

    op.create_table(
        "itens_vitrine",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vitrine_id", sa.Integer(), nullable=False),
        sa.Column("desenho_id", sa.Integer(), nullable=True),
        sa.Column("nome_snapshot", sa.String(length=255), nullable=False),
        sa.Column("preview_chave_snapshot", sa.String(length=512), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["desenho_id"], ["desenhos.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vitrine_id"], ["vitrines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vitrine_id", "desenho_id", name="uq_itens_vitrine_vitrine_desenho"),
    )
    op.create_index("ix_itens_vitrine_vitrine_id", "itens_vitrine", ["vitrine_id"])
    op.create_index("ix_itens_vitrine_desenho_id", "itens_vitrine", ["desenho_id"])


def downgrade() -> None:
    op.drop_index("ix_itens_vitrine_desenho_id", table_name="itens_vitrine")
    op.drop_index("ix_itens_vitrine_vitrine_id", table_name="itens_vitrine")
    op.drop_table("itens_vitrine")
    op.drop_index("ix_vitrines_expira_em", table_name="vitrines")
    op.drop_index("ix_vitrines_token", table_name="vitrines")
    op.drop_table("vitrines")
