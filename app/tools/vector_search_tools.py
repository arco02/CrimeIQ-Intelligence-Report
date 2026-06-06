from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from sentence_transformers import (
    SentenceTransformer
)

from app.config import (
    EMBEDDING_MODEL,
    TOP_K_VECTOR_RESULTS
)


class VectorSearchTools:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    def generate_query_embedding(
        self,
        query: str
    ):

        embedding = self.model.encode(query)

        return embedding.tolist()

    async def semantic_search(
        self,
        query: str,
        top_k: int = TOP_K_VECTOR_RESULTS
    ):

        embedding = self.generate_query_embedding(
            query
        )

        sql = text(
            """
            SELECT
                chunk_text,
                city,
                state,
                crime_type,
                year,
                embedding <=> CAST(:embedding AS vector)
                AS distance
            FROM text_chunks
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
            """
        )

        result = await self.db.execute(
            sql,
            {
                "embedding": str(embedding),
                "top_k": top_k
            }
        )

        rows = result.fetchall()

        return [
            {
                "chunk_text": row.chunk_text,
                "city": row.city,
                "state": row.state,
                "crime_type": row.crime_type,
                "year": row.year,
                "distance": float(row.distance)
            }
            for row in rows
        ]