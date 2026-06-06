from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NCRBRecord
from app.parsers.dataset_parser import DatasetParser


class IngestionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = DatasetParser()

    async def ingest_dataset(self):

        df = self.parser.parse()

        records = df.to_dict(orient="records")

        inserted_count = 0

        for row in records:

            stmt = insert(NCRBRecord).values(
                year=int(row["year"]),
                state=str(row["state"]),
                city=str(row["city"]),
                crime_type=str(row["crime_type"]),
                count=int(row["count"])
            )

            stmt = stmt.on_conflict_do_nothing(
                constraint="unique_crime_record"
            )

            result = await self.db.execute(stmt)

            if result.rowcount > 0:
                inserted_count += 1

        await self.db.commit()

        return {
            "status": "success",
            "inserted_records": inserted_count,
            "total_records": len(records)
        }