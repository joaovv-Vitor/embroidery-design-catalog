"""create catalog tables

Revision ID: 20260710_0001
Revises:
Create Date: 2026-07-10
"""

from alembic import op
import sqlalchemy as sa

revision = "20260710_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("cor", sa.String(32)),
        sa.Column("icone", sa.String(80)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("nome"),
    )
    op.create_table(
        "desenhos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categorias.id", ondelete="SET NULL")),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("imagem_preview_chave", sa.String(512)),
        sa.Column("favorito", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "arquivos_backup",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome_original", sa.String(255), nullable=False),
        sa.Column("nome_interno", sa.String(255), nullable=False),
        sa.Column("extensao", sa.String(16), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("tamanho_bytes", sa.BigInteger(), nullable=False),
        sa.Column("hash_sha256", sa.String(64), nullable=False),
        sa.Column("chave_storage", sa.String(512), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("hash_sha256"),
    )
    op.create_table(
        "origens_importacao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("identificacao", sa.String(255), nullable=False),
        sa.Column("tipo", sa.String(80), server_default=sa.text("'manual'"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "matrizes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("desenho_id", sa.Integer(), sa.ForeignKey("desenhos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("arquivo_backup_id", sa.Integer(), sa.ForeignKey("arquivos_backup.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("origem_importacao_id", sa.Integer(), sa.ForeignKey("origens_importacao.id", ondelete="SET NULL")),
        sa.Column("caminho_relativo_origem", sa.String(1024)),
        sa.Column("formato", sa.String(16), nullable=False),
        sa.Column("rotulo_tamanho", sa.String(120)),
        sa.Column("largura_mm", sa.Numeric(10, 2), nullable=False),
        sa.Column("altura_mm", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantidade_cores", sa.Integer(), nullable=False),
        sa.Column("quantidade_pontos", sa.Integer(), nullable=False),
        sa.Column("observacao", sa.Text()),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("arquivo_backup_id"),
    )
    op.create_index("ix_matrizes_desenho_id", "matrizes", ["desenho_id"])
    op.create_table(
        "importacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome_lote", sa.String(255), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("total_arquivos", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("arquivos_importados", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("arquivos_com_falha", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("iniciado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finalizado_em", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "itens_importacao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("importacao_id", sa.Integer(), sa.ForeignKey("importacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("matriz_id", sa.Integer(), sa.ForeignKey("matrizes.id", ondelete="SET NULL")),
        sa.Column("nome_arquivo", sa.String(255), nullable=False),
        sa.Column("caminho_relativo", sa.String(1024)),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("motivo_falha", sa.Text()),
        sa.Column("processado_em", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("matriz_id"),
    )


def downgrade() -> None:
    op.drop_table("itens_importacao")
    op.drop_table("importacoes")
    op.drop_index("ix_matrizes_desenho_id", table_name="matrizes")
    op.drop_table("matrizes")
    op.drop_table("origens_importacao")
    op.drop_table("arquivos_backup")
    op.drop_table("desenhos")
    op.drop_table("categorias")
