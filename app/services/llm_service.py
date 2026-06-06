from langchain_groq import ChatGroq

from app.config import (
    GROQ_API_KEY,
    MODEL_NAME
)


class LLMService:

    def __init__(self):

        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=MODEL_NAME,
            temperature=0.3
        )

    async def generate_response(
        self,
        prompt: str
    ):

        response = await self.llm.ainvoke(
            prompt
        )

        return response.content