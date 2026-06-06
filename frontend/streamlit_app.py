import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="CrimeIQ",
    layout="wide"
)

st.title("CrimeIQ")
st.subheader(
    "Agentic Crime Intelligence System"
)

query = st.text_area(
    "Enter your query"
)

if st.button("Run Analysis"):

    if not query:

        st.warning("Please enter a query.")

    else:

        with st.spinner("Processing..."):

            try:
                response = requests.post(
                    f"{API_BASE_URL}/query/",
                    json={
                        "query": query
                    }
                )

                if response.status_code != 200:
                    st.error(
                        f"Backend error {response.status_code}. "
                        f"Check the uvicorn terminal for details.\n\n"
                        f"{response.text[:500]}"
                    )
                    st.stop()

                data = response.json()

                st.markdown("## Response")

                st.write(
                    data.get("response")
                )

                st.markdown("---")

                st.markdown(
                    f"**Detected Intent:** "
                    f"{data.get('intent')}"
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the backend. "
                    "Make sure uvicorn is running on port 8000."
                )


if st.button("Generate Intelligence Report"):

    if not query:

        st.warning("Please enter a query.")

    else:

        with st.spinner(
            "Generating report..."
        ):

            try:
                response = requests.post(
                    f"{API_BASE_URL}/reports/generate",
                    json={
                        "query": query
                    }
                )

                if response.status_code != 200:
                    st.error(
                        f"Backend error {response.status_code}. "
                        f"Check the uvicorn terminal for details.\n\n"
                        f"{response.text[:500]}"
                    )
                    st.stop()

                data = response.json()

                report = data.get("report")

                if report:

                    st.success(
                        "Report generated successfully"
                    )

                    st.write(
                        report["file_path"]
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the backend. "
                    "Make sure uvicorn is running on port 8000."
                )