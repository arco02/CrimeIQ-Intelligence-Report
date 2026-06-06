import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://localhost:8000"

CRIME_TYPES = [
    "Crime Committed by Juveniles",
    "Crime against SC",
    "Crime against ST",
    "Crime against Senior Citizen",
    "Crime against children",
    "Crime against women",
    "Cyber Crimes",
    "Economic Offences",
    "Kidnapping",
    "Murder"
]

CITIES = [
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
    "Kochi",
    "Kolkata",
    "Kozhikode",
    "Lucknow",
    "Mumbai",
    "Nagpur",
    "Patna",
    "Pune",
    "Surat"
]

st.title("Crime Analytics")

analysis_type = st.selectbox(
    "Select Analysis Type",
    [
        "Crime Trend",
        "Top Crimes",
        "State Comparison"
    ]
)

# =========================
# TREND
# =========================

if analysis_type == "Crime Trend":

    city = st.selectbox("City", CITIES)

    crime_type = st.selectbox(
        "Crime Type",
        CRIME_TYPES
    )

    if st.button("Analyze Trend"):

        response = requests.get(
            f"{API_BASE_URL}/analysis/trend",
            params={
                "city": city,
                "crime_type": crime_type
            }
        )

        data = response.json()

        trend = data.get("trend", [])

        if trend:

            df = pd.DataFrame(trend)

            st.dataframe(df)

            fig = px.line(
                df,
                x="year",
                y="total_cases",
                markers=True,
                title=(
                    f"{crime_type} Trend "
                    f"in {city}"
                )
            )

            st.plotly_chart(
                fig,
                width='stretch'
            )

        else:
            st.warning(
                f"No trend data found for "
                f"{crime_type} in {city}."
            )


# =========================
# TOP CRIMES
# =========================

elif analysis_type == "Top Crimes":

    city = st.selectbox("City", CITIES)

    if st.button("Get Top Crimes"):

        response = requests.get(
            f"{API_BASE_URL}/analysis/top-crimes",
            params={
                "city": city
            }
        )

        data = response.json()

        crimes = data.get(
            "top_crimes",
            []
        )

        if crimes:

            df = pd.DataFrame(crimes)

            st.dataframe(df)

            fig = px.bar(
                df,
                x="crime_type",
                y="total_cases",
                title=(
                    f"Top Crimes in {city}"
                )
            )

            st.plotly_chart(
                fig,
                width='stretch'
            )

        else:
            st.warning(
                f"No crime data found for {city}."
            )


# =========================
# STATE COMPARISON
# =========================

elif analysis_type == "State Comparison":

    crime_type = st.selectbox(
        "Crime Type",
        CRIME_TYPES
    )

    if st.button("Compare States"):

        response = requests.get(
            f"{API_BASE_URL}/analysis/state-comparison",
            params={
                "crime_type": crime_type
            }
        )

        data = response.json()

        states = data.get(
            "states",
            []
        )

        if states:

            df = pd.DataFrame(states)

            st.dataframe(df)

            fig = px.bar(
                df,
                x="state",
                y="total_cases",
                title=(
                    f"State Comparison "
                    f"for {crime_type}"
                )
            )

            st.plotly_chart(
                fig,
                width='stretch'
            )

        else:
            st.warning(
                f"No state data found for {crime_type}."
            )