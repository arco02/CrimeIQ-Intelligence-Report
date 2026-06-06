from app.workflows.graph_builder import (
    build_graph
)


class OrchestratorAgent:

    def __init__(self, db):

        self.graph = build_graph(db)

    async def run(
        self,
        query: str
    ):

        initial_state = {
            "query": query,
            "intent": None,
            "city": None,
            "state": None,
            "crime_type": None,
            "analysis_result": None,
            "forecast_result": None,
            "clustering_result": None,
            "semantic_result": None,
            "final_response": None
        }

        result = await self.graph.ainvoke(
            initial_state
        )

        return result