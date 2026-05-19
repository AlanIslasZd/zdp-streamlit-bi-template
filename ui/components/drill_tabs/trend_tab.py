"""Trend Tab Renderer

Renders historical trend chart for metrics over time.
"""
import streamlit as st
import pandas as pd
import altair as alt

from services import snowflake_svc
from ui.components.formatters import FormatType, format_currency, format_number, format_percentage
from core.config import CACTUS


def render_trend_tab(metric_key: str, where_sql: str) -> None:
    """
    Render trend analysis tab with time-series chart.

    Args:
        metric_key: Registered metric key
        where_sql: WHERE clause from filters
    """
    from metrics import get_validated

    metric = get_validated(metric_key, ["drill_config"])
    trend_config = metric.drill_config.trend_config

    if not trend_config:
        st.warning("Trend configuration not available for this metric.")
        return

    st.markdown("### Historical Trend")

    # Granularity selector
    granularity = st.selectbox(
        "Time granularity:",
        options=["Daily", "Weekly", "Monthly"],
        index=["Daily", "Weekly", "Monthly"].index(trend_config.default_granularity),
        key=f"trend_granularity_{metric_key}"
    )

    with st.spinner("Loading trend data..."):
        try:
            # Fetch trend data from service layer
            trend_df = snowflake_svc.fetch_trend_data(
                where_sql=where_sql,
                date_col=trend_config.date_column,
                granularity=granularity
            )

            if trend_df.empty:
                st.info("No trend data available for selected filters.")
                return

            # Render chart
            _render_trend_chart(trend_df, granularity, trend_config.format_type)

        except Exception as e:
            st.error(f"Error loading trend data: {e}")
            st.exception(e)


def _render_trend_chart(df: pd.DataFrame, granularity: str, format_type: FormatType) -> None:
    """
    Render Altair line chart with dots for trend analysis.

    Args:
        df: DataFrame with columns PERIOD (datetime), LBL (str), VALUE (numeric)
        granularity: Time granularity for axis formatting
        format_type: How to format Y-axis and tooltips
    """
    df = df.copy()
    df.columns = df.columns.str.upper()

    # Format values for tooltips based on metric type
    if format_type == FormatType.PERCENTAGE:
        df["Metric"] = df["VALUE"].apply(lambda v: f"{v * 100:.1f}%" if pd.notna(v) else "N/A")
        y_axis_format = ".0%"
    elif format_type == FormatType.NUMBER:
        df["Metric"] = df["VALUE"].apply(lambda v: f"{int(v):,}" if pd.notna(v) else "N/A")
        y_axis_format = ",.0f"
    else:  # CURRENCY
        df["Metric"] = df["VALUE"].apply(lambda v: f"${v / 1e6:,.1f}M" if pd.notna(v) else "N/A")
        y_axis_format = "$,.0s"

    # Determine axis date format based on granularity
    if granularity == "Daily":
        axis_format = "%b %d"
    elif granularity == "Weekly":
        axis_format = "%b %d"
    else:  # Monthly
        axis_format = "%b %y"

    # Get axis values for tick marks
    axis_values = [pd.to_datetime(x).isoformat() for x in df['PERIOD'].unique()]

    # Create line chart
    line = alt.Chart(df).mark_line(
        color=CACTUS,
        strokeWidth=2.5,
        interpolate="monotone"
    ).encode(
        x=alt.X(
            "PERIOD:T",
            title=None,
            axis=alt.Axis(format=axis_format, labelAngle=-45, values=axis_values)
        ),
        y=alt.Y(
            "VALUE:Q",
            title=None,
            axis=alt.Axis(format=y_axis_format, gridColor="#333", gridDash=[3, 3])
        ),
        tooltip=[
            alt.Tooltip("LBL:N", title="Period"),
            alt.Tooltip("Metric:N", title="Value")
        ]
    )

    # Add dots on each point
    dots = alt.Chart(df).mark_circle(
        color=CACTUS,
        size=40
    ).encode(
        x="PERIOD:T",
        y="VALUE:Q",
        tooltip=[
            alt.Tooltip("LBL:N", title="Period"),
            alt.Tooltip("Metric:N", title="Value")
        ]
    )

    # Combine layers
    chart = (line + dots).properties(
        height=300
    ).configure_view(
        strokeWidth=0
    )

    st.altair_chart(chart, use_container_width=True)

    # Show data table in expander
    with st.expander("View as table"):
        tbl = df[["LBL", "Metric"]].copy()
        tbl.rename(columns={"LBL": "Period", "Metric": "Value"}, inplace=True)
        st.dataframe(tbl, use_container_width=True, hide_index=True)
