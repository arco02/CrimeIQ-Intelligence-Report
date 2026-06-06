from app.tools.db_tools import DBTools

from app.services.llm_service import (
    LLMService
)


class AnalysisAgent:

    def __init__(self, db):

        self.tools = DBTools(db)

        self.llm_service = LLMService()

    async def analyze_trend(
        self,
        city,
        crime_type,
        year_limit=None
    ):

        if city is None:

            return (
                "Please specify a city "
                "for trend analysis."
            )

        trend_data = await (
            self.tools.get_crime_trend(
                city,
                crime_type,
                year_limit
            )
        )

        if not trend_data:

            return (
                f"No trend data found "
                f"for {crime_type} in {city}."
            )

        formatted_data = [
            {
                "year": row[0],
                "count": row[1]
            }
            for row in trend_data
        ]

        prompt = f"""
        You are an AI crime analyst.

        Analyze the following crime trend data.

        City: {city}
        Crime Type: {crime_type}

        Trend Data:
        {formatted_data}

        Explain:
        - overall trend
        - whether crime is increasing/decreasing
        - any important fluctuations

        Keep answer concise and analytical.
        """

        summary = await (
            self.llm_service
            .generate_response(prompt)
        )

        return {
            "trend_data": formatted_data,
            "summary": summary
        }