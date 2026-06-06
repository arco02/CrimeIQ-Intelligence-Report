import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("Crime Intelligence Reports")

query = st.text_area(
    "Enter report query"
)

if st.button("Generate Report"):

    if not query:

        st.warning(
            "Please enter a query."
        )

    else:

        with st.spinner(
            "Generating report..."
        ):

            response = requests.post(
                f"{API_BASE_URL}/reports/generate",
                json={
                    "query": query
                }
            )

            data = response.json()

            report = data.get("report")

            if report:

                st.success(
                    "Report generated successfully"
                )

                st.write(
                    f"Title: {report['title']}"
                )

                st.write(
                    f"Path: {report['file_path']}"
                )