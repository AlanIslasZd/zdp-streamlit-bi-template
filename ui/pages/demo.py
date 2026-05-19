"""Demo Page - Shows One Metric with Drill-Down"""
import streamlit as st
import metrics as metric_registry
from ui.components.donut_card import render_donut_card
from ui.components.filters import render_filters


def render():
    """Main render function for demo page."""
    metric_registry.register_all()

    try:
        # Render filters in sidebar
        where_sql = render_filters(
            namespace="demo_page",
            available_filters=["region", "segment"],
            default_where="1=1"
        )

        # Page header
        st.header("📊 Demo Metrics Dashboard")
        st.markdown("This page demonstrates the metric registry pattern with one KPI card including drill-down.")

        # Render metric card
        col1, col2 = st.columns([1, 1])
        with col1:
            render_donut_card("demo_revenue", where_sql)

        with col2:
            st.info("👈 This metric card includes a drill-down modal! Click 'Details' to see breakdown by dimension.")
            st.markdown("""
            **Features demonstrated:**
            - 📊 Gauge chart with target pacing
            - 📈 YoY comparison
            - 🔍 Drill-down modal (click "Details")
            - 🎯 Attainment thresholds (green/yellow/red)
            - 🔄 Cached data fetching

            **To add another metric:**
            1. Register it in `metrics/definitions/demo.py`
            2. Call `render_donut_card("your_key", where_sql)`
            3. Done! The registry handles everything.
            """)

    except Exception as e:
        st.error("Error loading demo page.")
        st.exception(e)
