import asyncio

from app.api.dependencies import AsyncSessionLocal
from app.services.ingestion_service import IngestionService


async def main():

    async with AsyncSessionLocal() as session:

        ingestion_service = IngestionService(session)

        result = await ingestion_service.ingest_dataset()

        print("\nDataset Ingestion Complete")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())