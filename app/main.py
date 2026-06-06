from fastapi import FastAPI

from app.config import APP_NAME

from app.api.routes.ingest import (
    router as ingest_router
)

from app.api.routes.analysis import (
    router as analysis_router
)

from app.api.routes.prediction import (
    router as prediction_router
)

from app.api.routes.clustering import (
    router as clustering_router
)

from app.api.routes.query import (
    router as query_router
)

from app.api.routes.reports import (
    router as reports_router
)

app = FastAPI(
    title=APP_NAME
)

# =========================
# ROUTES
# =========================

app.include_router(
    ingest_router
)

app.include_router(
    analysis_router
)

app.include_router(
    prediction_router
)

app.include_router(
    clustering_router
)

app.include_router(
    query_router
)

app.include_router(
    reports_router
)

# =========================
# ROOT
# =========================

@app.get("/")
async def root():

    return {
        "app": APP_NAME,
        "status": "running"
    }