from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.tools.db_tools import DBTools

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.get("/trend")
async def get_crime_trend(
    city: str = Query(...),
    crime_type: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    tools = DBTools(db)

    result = await tools.get_crime_trend(
        city=city,
        crime_type=crime_type
    )

    return {
        "city": city,
        "crime_type": crime_type,
        "trend": [
            {
                "year": row.year,
                "total_cases": row.total_cases
            }
            for row in result
        ]
    }


@router.get("/top-crimes")
async def get_top_crimes(
    city: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    tools = DBTools(db)

    result = await tools.get_top_crimes_by_city(city)

    return {
        "city": city,
        "top_crimes": [
            {
                "crime_type": row.crime_type,
                "total_cases": row.total_cases
            }
            for row in result
        ]
    }


@router.get("/state-comparison")
async def state_comparison(
    crime_type: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    tools = DBTools(db)

    result = await tools.get_state_comparison(
        crime_type
    )

    return {
        "crime_type": crime_type,
        "states": [
            {
                "state": row.state,
                "total_cases": row.total_cases
            }
            for row in result
        ]
    }