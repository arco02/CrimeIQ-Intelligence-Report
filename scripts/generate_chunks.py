import asyncio

from app.api.dependencies import (
    AsyncSessionLocal
)

from app.services.chunk_service import (
    ChunkService
)

from app.services.embedding_service import (
    EmbeddingService
)


async def main():

    async with AsyncSessionLocal() as session:

        chunk_service = ChunkService(session)

        embedding_service = EmbeddingService(
            session
        )

        print("Generating chunks...")

        chunks = await chunk_service.generate_chunks()

        print(f"Generated {len(chunks)} chunks")

        print("Generating embeddings...")

        await embedding_service.store_chunks(
            chunks
        )

        print("Embeddings stored successfully")


if __name__ == "__main__":
    asyncio.run(main())