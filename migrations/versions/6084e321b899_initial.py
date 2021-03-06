"""initial

Revision ID: 6084e321b899
Revises: 
Create Date: 2021-02-13 23:11:30.653748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6084e321b899'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('search_string', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('zone',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('zone', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('domain',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain_name', sa.String(), nullable=True),
    sa.Column('zone_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['zone_id'], ['zone.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('registration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain_id', sa.Integer(), nullable=True),
    sa.Column('is_dead', sa.Boolean(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('added_date', sa.DateTime(), nullable=True),
    sa.Column('removed_date', sa.DateTime(), nullable=True),
    sa.Column('last_seen_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['domain_id'], ['domain.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hosted_country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('registration_id', sa.Integer(), nullable=True),
    sa.Column('country_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['country.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resource_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('registration_id', sa.Integer(), nullable=True),
    sa.Column('record_type', sa.Enum('a', 'cname', 'mx', 'ns', 'txt', name='resourcerecordtype'), nullable=True),
    sa.Column('priority', sa.String(), nullable=True),
    sa.Column('value', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['registration_id'], ['registration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resource_record')
    op.drop_table('hosted_country')
    op.drop_table('registration')
    op.drop_table('domain')
    op.drop_table('zone')
    op.drop_table('search')
    op.drop_table('country')
    # ### end Alembic commands ###
