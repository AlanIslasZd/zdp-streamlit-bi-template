"""
SessionManager - The Source of Truth for st.session_state

Centralized state management for the application.
All access to st.session_state must go through this class.
"""
import streamlit as st
from typing import List


class SessionManager:
    """
    Manages application state and filter logic.

    This class is the single source of truth for all session state,
    particularly for namespaced filters and computed WHERE clauses.
    """

    @staticmethod
    def initialize() -> None:
        """
        Initialize all session state variables.

        Must be called at the top of streamlit_app.py before any other session state access.
        Uses 'if key not in st.session_state' pattern to preserve state across reruns.
        """
        pass  # Filters are initialized on-demand by get_namespaced_filter

    # ==========================================
    # NAMESPACED FILTER METHODS
    # ==========================================

    @staticmethod
    def get_namespaced_filter(namespace: str, filter_key: str) -> List[str]:
        """
        Get filter value for a specific namespace.

        Args:
            namespace: Namespace identifier (e.g., "demo_page", "modal_demo_revenue")
            filter_key: Filter key without namespace (e.g., "filter_region")

        Returns:
            List of selected filter values for this namespace
        """
        key = f"{namespace}_{filter_key}"
        return st.session_state.get(key, [])

    @staticmethod
    def set_namespaced_filter(namespace: str, filter_key: str, value: List[str]) -> None:
        """
        Set filter value for a specific namespace.

        Args:
            namespace: Namespace identifier
            filter_key: Filter key without namespace
            value: New filter value (list of selected items)
        """
        key = f"{namespace}_{filter_key}"
        st.session_state[key] = value

    @staticmethod
    def reset_namespace_filters(namespace: str, filter_keys: List[str]) -> None:
        """
        Clear all filters for a specific namespace.

        Args:
            namespace: Namespace identifier
            filter_keys: List of filter keys to reset (e.g., ["filter_region", "filter_segment"])
        """
        for filter_key in filter_keys:
            key = f"{namespace}_{filter_key}"
            if key in st.session_state:
                st.session_state[key] = []

    @staticmethod
    def build_where_sql(
        namespace: str,
        available_filters: List[str],
        default_where: str = "1=1"
    ) -> str:
        """
        Build WHERE clause SQL from namespaced filter selections.

        Args:
            namespace: Namespace identifier
            available_filters: List of filter IDs (e.g., ["region", "segment"])
            default_where: Default WHERE clause when no filters active

        Returns:
            SQL WHERE clause string (e.g., "region_name IN ('Americas', 'EMEA')")
        """
        from core.filter_config import FILTER_CONFIGS

        conditions = []

        for filter_id in available_filters:
            if filter_id not in FILTER_CONFIGS:
                continue

            config = FILTER_CONFIGS[filter_id]
            values = SessionManager.get_namespaced_filter(namespace, config.session_key)

            if values:
                # Format values for SQL IN clause
                formatted_values = ", ".join([f"'{v}'" for v in values])
                conditions.append(f"{config.sql_column} IN ({formatted_values})")

        return " AND ".join(conditions) if conditions else default_where
