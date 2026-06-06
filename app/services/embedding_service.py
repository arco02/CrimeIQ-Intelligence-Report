from sentence_transformers import SentenceTransformer

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    EMBEDDING_MODEL
)

from app.models.db_models import TextChunk


class EmbeddingService:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    def generate_embedding(self, text: str):

        embedding = self.model.encode(text)

        return embedding.tolist()

    async def store_chunks(self, chunks):

        for chunk in chunks:

            embedding = self.generate_embedding(
                chunk["text"]
            )

            text_chunk = TextChunk(
                chunk_text=chunk["text"],
                embedding=embedding,
                year=chunk["year"],
                state=chunk["state"],
                city=chunk["city"],
                crime_type=chunk["crime_type"]
            )

            self.db.add(text_chunk)

        await self.db.commit()