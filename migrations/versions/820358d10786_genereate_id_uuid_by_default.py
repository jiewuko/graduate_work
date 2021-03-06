"""genereate id uuid by default

Revision ID: 820358d10786
Revises: 67684bfb026f
Create Date: 2021-07-20 19:03:40.146007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '820358d10786'
down_revision = '67684bfb026f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'cinema_together_room', ['id'])
    op.create_unique_constraint(None, 'cinema_together_room_user', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'cinema_together_room_user', type_='unique')
    op.drop_constraint(None, 'cinema_together_room', type_='unique')
    # ### end Alembic commands ###
