from langgraph.graph import (
    StateGraph,
    END
)

from app.workflows.state import (
    CrimeIQState
)

from app.workflows.nodes import (
    supervisor_node,
    analysis_node,
    comparison_node,
    forecast_node,
    clustering_node,
    semantic_node,
    risk_node
)


def build_graph(db):

    workflow = StateGraph(CrimeIQState)

    workflow.add_node(
        "supervisor",
        supervisor_node
    )

    async def analysis_wrapper(state):

        return await analysis_node(
            state,
            db
    )

    async def comparison_wrapper(state):

        return await comparison_node(
            state,
            db
        )
    
    async def risk_wrapper(state):

        return await risk_node(
            state,
            db
        )

    async def forecast_wrapper(state):

        return await forecast_node(
            state,
            db
        )


    async def clustering_wrapper(state):

        return await clustering_node(
            state,
            db
        )


    async def semantic_wrapper(state):

        return await semantic_node(
            state,
            db
        )


    workflow.add_node(
        "analysis",
        analysis_wrapper
    )

    workflow.add_node(
        "comparison",
        comparison_wrapper
    )

    workflow.add_node(
        "risk",
        risk_wrapper
    )

    workflow.add_node(
        "forecast",
        forecast_wrapper
    )

    workflow.add_node(
        "clustering",
        clustering_wrapper
    )

    workflow.add_node(
        "semantic",
        semantic_wrapper
    )

    workflow.set_entry_point(
        "supervisor"
    )

    def route(state):

        intent = state["intent"]

        if intent == "forecast":
            return "forecast"

        if intent == "clustering":
            return "clustering"

        if intent == "analysis":
            return "analysis"
        
        if intent == "comparison":
            return "comparison"
        
        if intent == "risk":
            return "risk"

        return "semantic"

    workflow.add_conditional_edges(
        "supervisor",
        route,
        {
            "forecast": "forecast",
            "clustering": "clustering",
            "analysis": "analysis",
            "comparison": "comparison",
            "semantic": "semantic",
            "risk": "risk"
        }
    )

    workflow.add_edge(
        "analysis",
        END
    )

    workflow.add_edge(
        "comparison",
        END
    )

    workflow.add_edge(
        "risk",
        END
    )

    workflow.add_edge(
        "forecast",
        END
    )

    workflow.add_edge(
        "clustering",
        END
    )

    workflow.add_edge(
        "semantic",
        END
    )

    return workflow.compile()