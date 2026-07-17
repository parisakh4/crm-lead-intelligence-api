"""cascade delete company children

Revision ID: 90b7b961f202
Revises: 7fd2f3db44c8
Create Date: 2026-07-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90b7b961f202'
down_revision = '7fd2f3db44c8'
branch_labels = None
depends_on = None


def _fk_name(inspector, table, referred_column='company_id'):
    for fk in inspector.get_foreign_keys(table):
        if referred_column in fk['constrained_columns']:
            return fk['name']
    raise RuntimeError(f"No foreign key on {table}.{referred_column} found")


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    for table in ('contact', 'opportunity'):
        fk_name = _fk_name(inspector, table)
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
            batch_op.create_foreign_key(
                fk_name, 'company', ['company_id'], ['id'], ondelete='CASCADE'
            )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    for table in ('contact', 'opportunity'):
        fk_name = _fk_name(inspector, table)
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
            batch_op.create_foreign_key(
                fk_name, 'company', ['company_id'], ['id']
            )
