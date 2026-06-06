import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("CrimeIQ AI Assistant")

query = st.text_area(
    "Ask a crime intelligence question"
)

if st.button("Submit Query"):

    if not query:

        st.warning(
            "Please enter a query."
        )

    else:

        with st.spinner(
            "Analyzing..."
        ):

            response = requests.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": query
                }
            )

            data = response.json()

            st.markdown(
                "## AI Response"
            )

            st.write(
                data.get("response")
            )

            st.markdown("---")

            st.write(
                f"Detected Intent: "
                f"{data.get('intent')}"
            )