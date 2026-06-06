from sqlalchemy.ext.asyncio import AsyncSession

from app.services.prediction_service import (
    PredictionService
)


class MLTools:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def forecast_crime(
        self,
        city: str,
        crime_type: str,
        years: int = 5

    ):

        prediction_service = PredictionService(
            self.db
        )

        result = await prediction_service.predict(
            city=city,
            crime_type=crime_type,
            years=years
        )

        return result