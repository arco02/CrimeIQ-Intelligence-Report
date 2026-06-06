import plotly.express as px
import pandas as pd


def line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str
):

    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        markers=True,
        title=title
    )

    return fig


def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str
):

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title
    )

    return fig


def scatter_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    hover_col: str,
    title: str
):

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        hover_name=hover_col,
        title=title
    )

    return fig