import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE_URL = "http://localhost:8000"

st.title("Crime Forecasting")

city = st.text_input("City")

crime_type = st.text_input(
    "Crime Type"
)

if st.button("Generate Forecast"):

    if not city or not crime_type:
        st.warning(
            "Please enter both a city and a crime type."
        )
        st.stop()

    with st.spinner("Generating forecast..."):

        response = requests.get(
            f"{API_BASE_URL}/prediction/forecast",
            params={
                "city": city,
                "crime_type": crime_type
            }
        )

        if response.status_code != 200:
            st.error(
                f"API error {response.status_code}: "
                f"{response.text}"
            )
            st.stop()

        data = response.json()

        forecast = data.get("forecast", [])

        if not forecast:
            st.warning(
                "No forecast data returned. "
                "Check that the city and crime type are valid."
            )
            st.stop()

        df = pd.DataFrame(forecast)

        # ── Summary metrics ───────────────────────────────────────
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "First Forecast Year",
            str(int(df["year"].iloc[0])),
            f"{int(df['prediction'].iloc[0]):,} cases"
        )

        col2.metric(
            "Last Forecast Year",
            str(int(df["year"].iloc[-1])),
            f"{int(df['prediction'].iloc[-1]):,} cases"
        )

        change_pct = (
            (df["prediction"].iloc[-1] - df["prediction"].iloc[0])
            / df["prediction"].iloc[0]
            * 100
        )

        col3.metric(
            "Projected Change",
            f"{change_pct:+.1f}%",
            delta_color=(
                "inverse" if change_pct > 0 else "normal"
            )
        )

        # ── Forecast chart with confidence bands ──────────────────
        fig = go.Figure()

        # Confidence interval — shaded band (lower → upper)
        fig.add_trace(
            go.Scatter(
                x=pd.concat(
                    [df["year"], df["year"].iloc[::-1]]
                ),
                y=pd.concat(
                    [df["upper_bound"], df["lower_bound"].iloc[::-1]]
                ),
                fill="toself",
                fillcolor="rgba(99, 110, 250, 0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="95% Confidence Interval",
                showlegend=True
            )
        )

        # Upper bound line (dashed, subtle)
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["upper_bound"],
                mode="lines",
                line=dict(
                    color="rgba(99, 110, 250, 0.4)",
                    dash="dot",
                    width=1
                ),
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Upper bound: %{y:,.0f}<extra></extra>"
                ),
                name="Upper Bound",
                showlegend=False
            )
        )

        # Lower bound line (dashed, subtle)
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["lower_bound"],
                mode="lines",
                line=dict(
                    color="rgba(99, 110, 250, 0.4)",
                    dash="dot",
                    width=1
                ),
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Lower bound: %{y:,.0f}<extra></extra>"
                ),
                name="Lower Bound",
                showlegend=False
            )
        )

        # Main prediction line
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["prediction"],
                mode="lines+markers",
                line=dict(
                    color="rgb(99, 110, 250)",
                    width=2.5
                ),
                marker=dict(size=7),
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Predicted: %{y:,.0f} cases<extra></extra>"
                ),
                name="Predicted Cases"
            )
        )

        fig.update_layout(
            title=dict(
                text=(
                    f"{crime_type} Forecast — {city}"
                    "<br><sup>Shaded band = 95% confidence interval</sup>"
                ),
                font=dict(size=16)
            ),
            xaxis=dict(
                title="Year",
                tickmode="linear",
                dtick=1
            ),
            yaxis=dict(
                title="Predicted Number of Cases",
                rangemode="tozero"
            ),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            width='stretch'
        )

        # ── Raw data table ────────────────────────────────────────
        with st.expander("Show raw forecast data"):

            display_df = df.copy()

            display_df.columns = [
                "Year",
                "Predicted Cases",
                "Lower Bound",
                "Upper Bound"
            ]

            display_df = display_df.set_index("Year")

            st.dataframe(
                display_df.style.format("{:,.0f}"),
                width='stretch'
            )