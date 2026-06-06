from app.agents.analysis_agent import (
    AnalysisAgent
)

from app.agents.clustering_agent import (
    ClusteringAgent
)

from app.tools.vector_search_tools import (
    VectorSearchTools
)

from app.agents.forecasting_agent import (
    ForecastAgent
)

from app.agents.comparison_agent import (
    ComparisonAgent
)

from app.agents.risk_agent import (
    RiskAgent
)

from app.services.llm_service import (
    LLMService
)

from app.config import GROQ_API_KEY

import re
import json
import logging

from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

# =========================
# INTENT DETECTION — LLM
# =========================

# Lightweight model for fast classification.
# Different from the main LLaMA-3.3-70B used for analysis.
INTENT_MODEL = "llama-3.1-8b-instant"

INTENT_PROMPT = """\
You are an intent classifier for CrimeIQ, an Indian crime analytics system \
that works with NCRB data across 19 metropolitan cities.

Classify the user's query into EXACTLY ONE of the following intents:

  forecast   – User wants a future prediction or projection of crime counts
               (e.g. "predict murder in Delhi for 2027", "forecast cyber crime")

  clustering – User wants to see how cities are grouped by danger/risk tier,
               or which cities are most dangerous overall
               (e.g. "cluster cities by crime", "which cities are most dangerous")

  analysis   – User wants a historical trend or top-crime breakdown for a city
               (e.g. "trend of robbery in Mumbai", "top crimes in Chennai",
               "how has kidnapping changed over the years in Kolkata")

  comparison – User wants to compare a crime type across multiple cities or states
               (e.g. "compare cyber crime across cities",
               "which city has the highest murder rate",
               "lowest theft — Mumbai or Delhi")

  risk       – User wants cities ranked by fastest growth rate or hotspot detection
               (e.g. "which cities have the highest growth in cyber crime",
               "fastest growing crime hotspots", "cities with rapidly increasing rape cases")

  semantic   – General, open-ended, or definitional questions that don't clearly
               fit any category above

Rules:
- If the query mentions a specific future year or uses "predict"/"forecast", prefer forecast.
- If it asks to *compare* a crime across multiple cities, prefer comparison over analysis.
- If it asks about *growth rate* or *hotspots*, prefer risk over analysis.
- Reply with ONLY a JSON object — no explanation, no markdown, no extra text.

Format:
{{"intent": "<one of: forecast | clustering | analysis | comparison | risk | semantic>"}}

User query: {query}"""


async def detect_intent_llm(query: str) -> str:
    """
    Use llama-3.1-8b-instant on Groq to classify the query intent.

    Returns one of:
        "forecast" | "clustering" | "analysis" |
        "comparison" | "risk" | "semantic"

    Falls back to keyword-based detection if the LLM call fails
    or returns an unexpected value.
    """
    valid_intents = {
        "forecast",
        "clustering",
        "analysis",
        "comparison",
        "risk",
        "semantic",
    }

    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=INTENT_MODEL,
            temperature=0,
            max_tokens=32,           # we only need a tiny JSON reply
        )

        response = await llm.ainvoke(
            INTENT_PROMPT.format(query=query)
        )

        raw = response.content.strip()

        # Strip optional ```json ... ``` fences some models add
        if "```" in raw:
            raw = raw.split("```")[1]
            raw = raw.lstrip("json").strip()

        data = json.loads(raw)
        intent = data.get("intent", "").lower().strip()

        if intent in valid_intents:
            logger.info(
                "LLM intent '%s' for query: %s",
                intent,
                query[:80]
            )
            return intent

        logger.warning(
            "LLM returned unknown intent '%s'; falling back to keywords.",
            intent
        )

    except Exception as exc:
        logger.warning(
            "LLM intent detection failed (%s); falling back to keywords.",
            exc
        )

    # Fallback — keyword-based (kept as safety net)
    return detect_intent_keyword(query)


# =========================
# INTENT DETECTION — KEYWORD FALLBACK
# =========================

def detect_intent_keyword(query: str) -> str:
    """
    Rule-based keyword intent classifier.
    Used as a fallback when the LLM call fails.
    """
    q = query.lower()

    if any(
        word in q
        for word in [
            "forecast",
            "predict",
            "future",
        ]
    ):
        return "forecast"

    if any(
        word in q
        for word in [
            "cluster",
            "dangerous"
        ]
    ):
        return "clustering"

    if any(
        word in q
        for word in [
            "risk",
            "growth",
            "fastest growing",
            "increasing rapidly",
            "hotspot"
        ]
    ):
        return "risk"

    if any(
        word in q
        for word in [
            "compare",
            "comparison",
            "across cities",
            "highest",
            "lowest"
        ]
    ):
        return "comparison"

    if any(
        word in q
        for word in [
            "trend",
            "top",
            "analysis"
        ]
    ):
        return "analysis"

    return "semantic"


# =========================
# ENTITY EXTRACTION
# =========================

# All 19 NCRB metropolitan cities.
# Listed longest-name-first within groups that share a prefix
# (e.g. "Kozhikode" before "Kochi") so the substring scan
# doesn't short-circuit on a partial match.
_CITIES = [
    "Ahmedabad",
    "Bengaluru",
    "Chennai",
    "Coimbatore",
    "Delhi",
    "Ghaziabad",
    "Hyderabad",
    "Indore",
    "Jaipur",
    "Kanpur",
    "Kozhikode",   # must come before "Kochi"
    "Kochi",
    "Kolkata",
    "Lucknow",
    "Mumbai",
    "Nagpur",
    "Patna",
    "Pune",
    "Surat",
]

# Common aliases / alternate spellings users might type
_CITY_ALIASES = {
    "bangalore":  "Bengaluru",
    "bombay":     "Mumbai",
    "calcutta":   "Kolkata",
    "madras":     "Chennai",
    "new delhi":  "Delhi",
    "ncr":        "Delhi",
    "cochin":     "Kochi",
    "calicut":    "Kozhikode",
    "ghaziyabad": "Ghaziabad",
}


def extract_city(query: str):
    """
    Return the canonical city name found in *query*, or None.

    Matching is case-insensitive and whole-word so that e.g.
    'Pune' doesn't trigger inside 'Punishment'.
    Aliases are resolved before the canonical list is checked.
    """
    q = query.lower()

    # 1. Check aliases first
    for alias, canonical in _CITY_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, q):
            return canonical

    # 2. Check canonical names (whole-word, case-insensitive)
    for city in _CITIES:
        pattern = r'\b' + re.escape(city.lower()) + r'\b'
        if re.search(pattern, q):
            return city

    return None


def extract_crime_type(query: str):

    q = query.lower()

    aliases = {

        # Murder
        "murder": "Murder",
        "murders": "Murder",
        "homicide": "Murder",
        "killing": "Murder",
        "killings": "Murder",

        # Kidnapping
        "kidnapping": "Kidnapping",
        "kidnap": "Kidnapping",
        "abduction": "Kidnapping",
        "abductions": "Kidnapping",

        # Crime against women
        "crime against women": "Crime against women",
        "women crime": "Crime against women",
        "women crimes": "Crime against women",
        "women safety": "Crime against women",
        "rape": "Crime against women",
        "sexual assault": "Crime against women",
        "violence against women": "Crime against women",

        # Crime against children
        "crime against children": "Crime against children",
        "child crime": "Crime against children",
        "child crimes": "Crime against children",
        "children crime": "Crime against children",
        "child abuse": "Crime against children",
        "crimes against children": "Crime against children",

        # Juvenile crime
        "juvenile": "Crime Committed by Juveniles",
        "juvenile crime": "Crime Committed by Juveniles",
        "juvenile crimes": "Crime Committed by Juveniles",
        "crimes by juveniles": "Crime Committed by Juveniles",
        "youth crime": "Crime Committed by Juveniles",

        # Senior citizen
        "crime against senior citizen": "Crime against Senior Citizen",
        "senior citizen": "Crime against Senior Citizen",
        "elder crime": "Crime against Senior Citizen",
        "elderly crime": "Crime against Senior Citizen",
        "crimes against elderly": "Crime against Senior Citizen",

        # SC
        "crime against sc": "Crime against SC",
        "sc crime": "Crime against SC",
        "scheduled caste": "Crime against SC",
        "dalit crime": "Crime against SC",
        "crimes against sc": "Crime against SC",

        # ST
        "crime against st": "Crime against ST",
        "st crime": "Crime against ST",
        "scheduled tribe": "Crime against ST",
        "tribal crime": "Crime against ST",
        "crimes against st": "Crime against ST",

        # Economic offences
        "economic offence": "Economic Offences",
        "economic offences": "Economic Offences",
        "economic offense": "Economic Offences",
        "economic offenses": "Economic Offences",
        "financial crime": "Economic Offences",
        "fraud": "Economic Offences",
        "white collar": "Economic Offences",
        "white collar crime": "Economic Offences",

        # Cyber crimes
        "cyber crime": "Cyber Crimes",
        "cyber crimes": "Cyber Crimes",
        "cybercrime": "Cyber Crimes",
        "cybercrimes": "Cyber Crimes",
        "hacking": "Cyber Crimes",
        "online fraud": "Cyber Crimes",
        "internet crime": "Cyber Crimes",
        "digital crime": "Cyber Crimes",
    }

    for alias in sorted(aliases, key=len, reverse=True):
        if alias in q:
            return aliases[alias]

    return None


def extract_year_limit(query: str):

    q = query.lower()

    LATEST_DATA_YEAR = 2023

    # --- Duration patterns ("last 3 years", "next 5 years") ---
    # These return a year COUNT directly
    duration_patterns = [
        r'last\s+(\d+)\s+years',
        r'next\s+(\d+)\s+years',
        r'for\s+next\s+(\d+)\s+years',
        r'for\s+(\d+)\s+years'
    ]

    for pattern in duration_patterns:
        match = re.search(pattern, q)
        if match:
            return int(match.group(1))

    # --- Target year patterns ("till 2027", "for 2027", "in 2027") ---
    # These specify a destination year — convert to a count
    target_year_match = re.search(
        r'(?:till|until|through|upto|up to|for|in)\s+(20\d{2})',
        q
    )

    if target_year_match:
        target_year = int(target_year_match.group(1))
        years = target_year - LATEST_DATA_YEAR + 1
        if years > 0:
            return years

    return None


# =========================
# NODES
# =========================

async def supervisor_node(state):
    """
    Entry-point node: detects intent using the LLM, then
    extracts city, crime type, and year limit from the query.
    """
    query = state["query"]

    # LLM-based intent detection (falls back to keywords on failure)
    intent = await detect_intent_llm(query)

    city = extract_city(query)
    crime_type = extract_crime_type(query)
    year_limit = extract_year_limit(query)

    return {
        **state,
        "intent": intent,
        "city": city,
        "crime_type": crime_type,
        "year_limit": year_limit
    }


async def analysis_node(state, db):

    agent = AnalysisAgent(db)

    result = await agent.analyze_trend(
        city=state["city"],
        crime_type=state["crime_type"],
        year_limit=state.get("year_limit")
    )

    return {
        **state,
        "analysis_result": result,
        "final_response": result
    }


async def comparison_node(state, db):

    crime_type = state.get("crime_type")

    if not crime_type:
        return {
            **state,
            "final_response": (
                "Please specify a crime type for city comparison "
                "(e.g. 'compare murder across cities')."
            )
        }

    agent = ComparisonAgent(db)

    result = await agent.compare_cities(
        crime_type=crime_type
    )

    return {
        **state,
        "comparison_result": result,
        "final_response": result
    }


async def risk_node(state, db):

    crime_type = state.get("crime_type")

    if not crime_type:
        return {
            **state,
            "final_response": (
                "Please specify a crime type for risk analysis "
                "(e.g. 'which cities have the fastest growing cyber crime')."
            )
        }

    agent = RiskAgent(db)

    result = await agent.identify_high_growth_cities(
        crime_type=crime_type
    )

    return {
        **state,
        "risk_result": result,
        "final_response": result
    }


async def forecast_node(state, db):

    agent = ForecastAgent(db)

    result = await agent.forecast_crime(
        city=state["city"],
        crime_type=state["crime_type"],
        years=state.get(
            "year_limit",
            5
        )
    )

    return {
        **state,
        "forecast_result": result,
        "final_response": result
    }


async def clustering_node(state, db):

    agent = ClusteringAgent(db)

    result = await agent.analyze_city_risk()

    return {
        **state,
        "clustering_result": result,
        "final_response": result
    }


async def semantic_node(state, db):
    """
    Semantic RAG node: retrieves relevant chunks via pgvector,
    then synthesises a natural-language answer using the LLM.
    """
    tools = VectorSearchTools(db)

    chunks = await tools.semantic_search(
        state["query"]
    )

    if not chunks:
        return {
            **state,
            "semantic_result": "",
            "final_response": (
                "No relevant crime data found for your query."
            )
        }

    # Build context from retrieved chunks
    context = "\n".join(
        item["chunk_text"] for item in chunks
    )

    # Synthesise a natural-language answer instead of
    # returning raw chunk text to the user
    prompt = f"""\
You are CrimeIQ, an AI crime analyst for Indian cities.

Answer the user's question using ONLY the data excerpts below.
Be concise, factual, and cite specific numbers where available.
If the data is insufficient, say so clearly.

--- RETRIEVED DATA ---
{context}
----------------------

User question: {state["query"]}
"""

    llm_service = LLMService()

    answer = await llm_service.generate_response(prompt)

    return {
        **state,
        "semantic_result": context,
        "final_response": answer
    }