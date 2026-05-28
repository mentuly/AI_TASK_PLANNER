from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, func
from core.db_models.metadata import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("telegram_id", BigInteger, unique=True, nullable=False),
    Column("username", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
