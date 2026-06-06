import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://localhost:8000"

st.title("City Risk Clustering")

if st.button("Run Clustering"):

    response = requests.post(
        f"{API_BASE_URL}/clustering/cities"
    )

    data = response.json()

    clusters = data.get(
        "clusters",
        []
    )

    if clusters:

        df = pd.DataFrame(clusters)

        st.dataframe(df)

        fig = px.scatter(
            df,
            x="cluster_id",
            y="risk_score",
            color="risk_tier",
            hover_name="city",
            title="City Risk Clusters"
        )

        st.plotly_chart(
            fig,
            width='stretch'
        )