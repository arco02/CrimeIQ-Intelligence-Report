import asyncio

from sqlalchemy import text

from app.api.dependencies import engine
from app.models.db_models import Base


async def setup_database():
    async with engine.begin() as conn:
        await conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        await conn.run_sync(Base.metadata.create_all)

    print("Database setup complete.")


if __name__ == "__main__":
    asyncio.run(setup_database())