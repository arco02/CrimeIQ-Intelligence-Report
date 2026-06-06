from app.tools.db_tools import (
    DBTools
)

from app.services.llm_service import (
    LLMService
)


class ComparisonAgent:

    def __init__(self, db):

        self.tools = DBTools(db)

        self.llm_service = LLMService()

    async def compare_cities(
        self,
        crime_type
    ):

        data = await (
            self.tools
            .compare_crime_across_cities(
                crime_type
            )
        )

        if not data:

            return (
                f"No comparison data found "
                f"for {crime_type}."
            )

        prompt = f"""
        You are an AI crime analyst.

        Analyze the following city-wise
        crime comparison data.

        Crime Type:
        {crime_type}

        Data:
        {data}

        Explain:
        - which cities have highest crime
        - which cities have lower crime
        - important observations
        - overall pattern

        Keep response analytical and concise.
        """

        summary = await (
            self.llm_service
            .generate_response(prompt)
        )

        return {
            "comparison_data": data,
            "summary": summary
        }