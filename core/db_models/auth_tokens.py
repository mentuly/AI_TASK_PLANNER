from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, func
from core.db_models.metadata import metadata

auth_tokens = Table(
    "auth_tokens",
    metadata,
    Column("token", String, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
