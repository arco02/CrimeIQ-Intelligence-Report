from typing import TypedDict, Optional


class CrimeIQState(TypedDict):

    query: str

    intent: Optional[str]

    city: Optional[str]

    state: Optional[str]

    crime_type: Optional[str]

    year_limit: Optional[int]

    analysis_result: Optional[str]

    forecast_result: Optional[list]

    clustering_result: Optional[str]

    comparison_result: Optional[dict]   

    risk_result: Optional[dict]

    semantic_result: Optional[str]

    final_response: Optional[str]