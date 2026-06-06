from app.tools.ml_tools import (
    MLTools
)

from app.services.llm_service import (
    LLMService
)


class ForecastAgent:

    def __init__(self, db):

        self.tools = MLTools(db)

        self.llm_service = LLMService()

    async def forecast_crime(
        self,
        city,
        crime_type,
        years=5
    ):

        forecast = await (
            self.tools.forecast_crime(
                city=city,
                crime_type=crime_type,
                years=years
            )
        )

        if not forecast:

            return (
                f"No forecasting data found "
                f"for {crime_type} in {city}."
            )

        prompt = f"""
        You are an AI crime analyst.

        Analyze the following crime forecast data.

        City: {city}
        Crime Type: {crime_type}

        Forecast Data:
        {forecast}

        Explain:
        - overall trend
        - whether crime is increasing/decreasing
        - future outlook
        - important observations

        Keep response concise and analytical.
        """

        summary = await (
            self.llm_service
            .generate_response(prompt)
        )

        return {
            "forecast_data": forecast,
            "summary": summary
        }