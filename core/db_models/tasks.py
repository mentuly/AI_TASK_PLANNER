from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy import false
from core.db_models.metadata import metadata

tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("title", String, nullable=False),
    Column("is_done", Boolean, nullable=False, server_default=false()),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
