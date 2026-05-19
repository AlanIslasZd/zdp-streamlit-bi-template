"""Donut Card Component

Registry-driven metric card with gauge chart, delta, YoY, and drill-down.
"""
import streamlit as st
import plotly.graph_objects as go

from metrics import get_validated
from ui.components.formatters import format_value, format_delta, get_attainment_color
from ui.components.drill_modal_v2 import open_drill_modal
from ui.components import drill_button
from core.config import DEFAULT_THRESHOLDS


def render_donut_card(metric_key: str, where_sql: str) -> None:
    """
    Render metric card with gauge, delta, YoY, and drill button.

    Args:
        metric_key: Metric registry key
        where_sql: WHERE clause from SessionManager
    """
    metric = get_validated(metric_key, required_configs=["donut_config"])
    donut = metric.donut_config

    # Fetch data
    df = donut.service_fn(where_sql)
    if df.empty:
        st.warning(f"No data for {metric.title}")
        return

    row = df.iloc[0].fillna(0)

    # Extract values
    actual = float(row[donut.actual_col])
    target = float(row[donut.target_qtd_col]) if donut.target_qtd_col else 0.0

    # Calculate percentage and attainment
    pct = (actual / target) if target != 0 else 0.0
    thresholds = donut.thresholds or DEFAULT_THRESHOLDS
    color = get_attainment_color(pct, thresholds)

    # Format values
    display_val = format_value(actual, donut.format_type)
    target_text = format_value(target, donut.format_type) if target != 0 else None

    # YoY calculation
    yoy_text = ""
    if metric.show_yoy and donut.yoy_actual_col and donut.yoy_ly_col:
        current = float(row.get(donut.yoy_actual_col, 0))
        last_year = float(row.get(donut.yoy_ly_col, 0))
        if last_year != 0:
            yoy_delta = (current - last_year) / last_year
            yoy_text = format_delta(yoy_delta, donut.yoy_format)

    # Render title
    title_html = f"<div style='font-size:15px; font-weight:500; color:#FFFFFF; margin-bottom:5px;'>{metric.title}</div>"
    st.markdown(title_html, unsafe_allow_html=True)

    # Layout: value + gauge
    val_col, gauge_col = st.columns([1.3, 1])

    with val_col:
        # Show value with delta if target exists
        if target_text:
            delta_text = f"Target: {target_text}"
            st.metric(label="Value", value=display_val, delta=delta_text, label_visibility="collapsed")
        else:
            st.metric(label="Value", value=display_val, label_visibility="collapsed")

        # Show YoY if available
        if yoy_text:
            st.caption(f"YoY: {yoy_text}")

        # Show help text if available
        if metric.help_text:
            st.caption(metric.help_text)

    with gauge_col:
        # Render gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct * 100,
            number={'suffix': "%", 'font': {'size': 20, 'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, 120], 'tickwidth': 1, 'tickcolor': color},
                'bar': {'color': color},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 2,
                'bordercolor': color,
            }
        ))
        fig.update_layout(
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    # Drill button
    if metric.drill_config:
        if drill_button.render_drill_button(metric.drill_config.drill_key, "Details"):
            open_drill_modal(metric.key, where_sql)
    else:
        st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
