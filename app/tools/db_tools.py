from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NCRBRecord
from sqlalchemy import (
    select,
    func,
    desc
)

class DBTools:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_top_crimes_by_city(
        self,
        city: str,
        limit: int = 10
    ):

        stmt = (
            select(
                NCRBRecord.crime_type,
                func.sum(NCRBRecord.count).label("total_cases")
            )
            .where(
                func.lower(NCRBRecord.city)
                == city.lower()
            )
            .group_by(NCRBRecord.crime_type)
            .order_by(
                func.sum(NCRBRecord.count).desc()
            )
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        return result.all()

    async def get_crime_trend(
        self,
        city: str,
        crime_type: str,
        year_limit = None
    ):

        if city is None:
            return []
    
        stmt = (
            select(
                NCRBRecord.year,
                func.sum(NCRBRecord.count).label("total_cases")
            )
            .where(
                func.lower(NCRBRecord.city)
                == city.lower(),
                func.lower(NCRBRecord.crime_type)
                == crime_type.lower()
            )
            .group_by(NCRBRecord.year)
            .order_by(NCRBRecord.year)
        )

        result = await self.db.execute(stmt)
        rows = result.all()
        if year_limit:
            rows = rows[-year_limit:]

        return rows

    async def get_state_comparison(
        self,
        crime_type: str
    ):

        stmt = (
            select(
                NCRBRecord.state,
                func.sum(NCRBRecord.count).label("total_cases")
            )
            .where(
                func.lower(NCRBRecord.crime_type)
                == crime_type.lower()
            )
            .group_by(NCRBRecord.state)
            .order_by(
                func.sum(NCRBRecord.count).desc()
            )
        )

        result = await self.db.execute(stmt)

        return result.all()

    async def get_available_cities(self):

        stmt = (
            select(NCRBRecord.city)
            .distinct()
            .order_by(NCRBRecord.city)
        )

        result = await self.db.execute(stmt)

        return [row[0] for row in result.all()]

    async def get_available_crime_types(self):

        stmt = (
            select(NCRBRecord.crime_type)
            .distinct()
            .order_by(NCRBRecord.crime_type)
        )

        result = await self.db.execute(stmt)

        return [row[0] for row in result.all()]
    
    async def compare_crime_across_cities(
    self,
    crime_type
    ):

        stmt = (
            select(
                NCRBRecord.city,
                func.sum(
                    NCRBRecord.count
                ).label("total_cases")
            )
            .where(
                func.lower(
                    NCRBRecord.crime_type
                )
                == crime_type.lower()
            )
            .group_by(
                NCRBRecord.city
            )
            .order_by(
                desc("total_cases")
            )
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        return [
            {
                "city": row[0],
                "total_cases": int(row[1])
            }
            for row in rows
        ]
    
    async def get_city_growth_rates(
        self,
        crime_type: str
    ):

        stmt = (
            select(
                NCRBRecord.city,
                NCRBRecord.year,
                NCRBRecord.count
            )
            .where(
                func.lower(
                    NCRBRecord.crime_type
                )
                == crime_type.lower()
            )
            .order_by(
                NCRBRecord.city,
                NCRBRecord.year
            )
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        city_data = {}

        for city, year, count in rows:

            if city not in city_data:
                city_data[city] = []

            city_data[city].append(
                {
                    "year": year,
                    "count": count
                }
            )

        growth_results = []

        for city, values in city_data.items():

            if len(values) < 2:
                continue

            first_count = values[0]["count"]
            last_count = values[-1]["count"]

            if first_count == 0:
                continue

            growth_rate = (
                (
                    last_count - first_count
                )
                / first_count
            ) * 100

            growth_results.append(
                {
                    "city": city,
                    "growth_rate": round(
                        growth_rate,
                        2
                    ),
                    "start_count": first_count,
                    "latest_count": last_count
                }
            )

        growth_results.sort(
            key=lambda x: x["growth_rate"],
            reverse=True
        )

        return growth_results