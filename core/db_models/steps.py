from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy import false
from core.db_models.metadata import metadata

steps = Table(
    "steps",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("minutes", Integer, nullable=False),
    Column("is_done", Boolean, nullable=False, server_default=false()),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
