"""Filter Components

Renders filter sidebar and manages filter state through SessionManager.
"""
import streamlit as st
from typing import List
from core.session import SessionManager
from core.filter_config import FILTER_CONFIGS


def render_filters(
    namespace: str,
    available_filters: List[str],
    default_where: str = "1=1"
) -> str:
    """
    Render filter sidebar and return WHERE SQL clause.

    Args:
        namespace: Namespace for filter state (e.g., "demo_page")
        available_filters: List of filter IDs to show (e.g., ["region", "segment"])
        default_where: Default WHERE clause when no filters active

    Returns:
        SQL WHERE clause string
    """
    with st.sidebar:
        st.header("🔍 Filters")

        for filter_id in available_filters:
            if filter_id not in FILTER_CONFIGS:
                continue

            config = FILTER_CONFIGS[filter_id]

            # Get current selection
            current_values = SessionManager.get_namespaced_filter(namespace, config.session_key)

            # Render multiselect
            selected = st.multiselect(
                label=config.label,
                options=config.options,
                default=current_values,
                key=f"{namespace}_{filter_id}_widget"
            )

            # Update session state
            SessionManager.set_namespaced_filter(namespace, config.session_key, selected)

        # Reset button
        if st.button("🔄 Reset Filters", key=f"{namespace}_reset"):
            filter_keys = [FILTER_CONFIGS[f].session_key for f in available_filters if f in FILTER_CONFIGS]
            SessionManager.reset_namespace_filters(namespace, filter_keys)
            st.rerun()

    # Build WHERE clause
    return SessionManager.build_where_sql(namespace, available_filters, default_where)
