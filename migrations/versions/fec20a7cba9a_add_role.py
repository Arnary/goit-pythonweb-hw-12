"""add role

Revision ID: fec20a7cba9a
Revises: 103e114c6f6f
Create Date: 2024-12-27 15:04:50.595653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fec20a7cba9a'
down_revision: Union[str, None] = '103e114c6f6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    user_role_enum = sa.Enum("USER", "ADMIN", name="userrole")
    user_role_enum.create(op.get_bind())

    op.add_column(
        "users",
        sa.Column("role", user_role_enum, nullable=False, server_default="USER"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "role")

    user_role_enum = sa.Enum("USER", "ADMIN", name="userrole")
    user_role_enum.drop(op.get_bind())
    # ### end Alembic commands ###