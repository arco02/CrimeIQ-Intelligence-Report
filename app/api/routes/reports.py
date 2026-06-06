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

from app.agents.report_agent import (
    ReportAgent
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/generate")
async def generate_report(
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

    workflow_result = await orchestrator.run(
        query
    )

    analysis = workflow_result.get(
        "final_response"
    )

    report_agent = ReportAgent()

    report = (
        report_agent.generate_intelligence_report(
            query=query,
            analysis=analysis
        )
    )

    return {
        "query": query,
        "report": report
    }