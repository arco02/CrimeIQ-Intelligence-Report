from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.api.dependencies import (
    get_db
)

from app.agents.orchestrator import (
    OrchestratorAgent
)

router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


@router.post("/")
async def query_agent(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):

    query = payload.get("query")

    if not query:

        return {
            "error": "Query is required"
        }

    orchestrator = OrchestratorAgent(
        db
    )

    result = await orchestrator.run(
        query
    )

    return {
        "query": query,
        "intent": result.get("intent"),
        "response": result.get(
            "final_response"
        )
    }