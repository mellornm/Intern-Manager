from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Common base class for all SQLAlchemy models in the application.

    Uses SQLAlchemy 2.0 style declarative mapping and attaches the custom
    metadata naming convention required for stable migrations on SQLite.
    """

    metadata = MetaData(naming_convention=naming_convention)
