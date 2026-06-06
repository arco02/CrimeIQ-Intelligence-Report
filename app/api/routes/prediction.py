from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db

from app.tools.ml_tools import MLTools

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


@router.get("/forecast")
async def forecast_crime(
    city: str = Query(...),
    crime_type: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    ml_tools = MLTools(db)

    predictions = await ml_tools.forecast_crime(
        city=city,
        crime_type=crime_type
    )

    return {
        "city": city,
        "crime_type": crime_type,
        "forecast": predictions
    }