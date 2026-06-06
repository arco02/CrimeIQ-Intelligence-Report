from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NCRBRecord


class ChunkService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_chunks(self):

        stmt = select(NCRBRecord)

        result = await self.db.execute(stmt)

        records = result.scalars().all()

        chunks = []

        for record in records:

            chunk = (
                f"In {record.year}, "
                f"{record.city}, {record.state} "
                f"reported {record.count} cases of "
                f"{record.crime_type}."
            )

            chunks.append({
                "text": chunk,
                "year": record.year,
                "state": record.state,
                "city": record.city,
                "crime_type": record.crime_type
            })

        return chunks