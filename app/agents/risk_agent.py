from app.tools.db_tools import DBTools


class RiskAgent:

    def __init__(self, db):

        self.tools = DBTools(db)

    async def identify_high_growth_cities(
        self,
        crime_type
    ):

        growth_data = (
            await self.tools.get_city_growth_rates(
                crime_type
            )
        )

        top_cities = growth_data[:5]

        return {
            "crime_type": crime_type,
            "high_growth_cities": top_cities
        }