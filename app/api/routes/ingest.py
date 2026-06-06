from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.services.ingestion_service import IngestionService

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"]
)


@router.post("/")
async def ingest_dataset(
    db: AsyncSession = Depends(get_db)
):

    service = IngestionService(db)

    result = await service.ingest_dataset()

    return result