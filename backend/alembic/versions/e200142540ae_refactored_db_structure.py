"""refactored db structure

Revision ID: e200142540ae
Revises: b979e3b2d27d
Create Date: 2024-06-10 18:26:51.540328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e200142540ae'
down_revision: Union[str, None] = 'b979e3b2d27d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ai_match_histories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('ai_type', sa.String(), nullable=False),
    sa.Column('match_id', sa.UUID(), nullable=False),
    sa.Column('score', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('matches',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('match_date', sa.DateTime(), nullable=True),
    sa.Column('room_socket_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_match_histories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_kinde_uuid', sa.String(), nullable=False),
    sa.Column('match_id', sa.UUID(), nullable=False),
    sa.Column('score', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('kinde_uuid', sa.String(), nullable=False),
    sa.Column('profile_picture', sa.String(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('user_total_score', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('highscores')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('highscores',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('highscore_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('user_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_score', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('room_socket_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('ai_bot_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('kinde_uuid', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('profile_picture', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='highscores_pkey')
    )
    op.drop_table('users')
    op.drop_table('user_match_histories')
    op.drop_table('matches')
    op.drop_table('ai_match_histories')
    # ### end Alembic commands ###
