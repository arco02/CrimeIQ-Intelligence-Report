from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db

from app.services.clustering_service import (
    ClusteringService
)

router = APIRouter(
    prefix="/clustering",
    tags=["Clustering"]
)


@router.post("/cities")
async def cluster_cities(
    db: AsyncSession = Depends(get_db)
):

    service = ClusteringService(db)

    result = await service.cluster_cities()

    return {
        "status": "success",
        "clusters": result
    }