"""Registry-driven drill modal orchestrator.

Dispatches drill tabs to their renderers based on metric configuration.
"""
import streamlit as st

from metrics import get_validated
from ui.components.drill_tabs.breakdown_tab import render_breakdown_tab
from ui.components.drill_tabs.trend_tab import render_trend_tab


@st.dialog("Metric Deep Dive", width="large")
def open_drill_modal(metric_key: str, where_sql: str) -> None:
    """
    Open the registry-driven drill modal for a metric.

    Args:
        metric_key: Registered metric key (must have drill_config).
        where_sql: WHERE clause from the page-level filters.
    """
    metric = get_validated(metric_key, ["drill_config"])
    config = metric.drill_config

    st.subheader(f"Deep Dive: {config.drill_title}")

    # Use page-level WHERE clause (no additional modal filters in this template)
    modal_where_sql = where_sql

    # Append metric-specific WHERE clause if defined
    if metric.extra_where:
        modal_where_sql = f"{modal_where_sql} AND ({metric.extra_where})"

    # Build tab configuration
    tab_configs = []
    if "breakdown" in config.tabs:
        tab_configs.append(("Breakdown", "breakdown"))
    if "trend" in config.tabs:
        tab_configs.append(("Trend", "trend"))

    # Create tabs
    if not tab_configs:
        st.warning("No tabs configured for this metric.")
        return

    tab_labels = [label for label, _ in tab_configs]
    tabs = st.tabs(tab_labels)

    # Render each tab
    for idx, (label, tab_id) in enumerate(tab_configs):
        with tabs[idx]:
            if tab_id == "breakdown":
                render_breakdown_tab(metric_key, modal_where_sql)
            elif tab_id == "trend":
                render_trend_tab(metric_key, modal_where_sql)
