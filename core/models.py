from core.db import get_engine
from core.db_models.metadata import metadata

from core.db_models.users import users
from core.db_models.auth_tokens import auth_tokens
from core.db_models.tasks import tasks
from core.db_models.steps import steps


async def init_db():
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
