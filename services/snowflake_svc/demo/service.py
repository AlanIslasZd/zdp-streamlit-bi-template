"""Demo Service Functions"""
import streamlit as st
import pandas as pd
from . import sql
from ..session import get_snowflake_session


@st.cache_data(ttl=3600)
def fetch_demo_kpi(where_sql: str) -> pd.DataFrame:
    """
    Fetch demo KPI with filters.

    Args:
        where_sql: WHERE clause from SessionManager

    Returns:
        DataFrame with columns: METRIC_VALUE, TARGET, ACTUAL_LY
    """
    session = get_snowflake_session()

    # Mock data for local development
    if session is None:
        return pd.DataFrame({
            'METRIC_VALUE': [1_250_000],
            'TARGET': [1_200_000],
            'ACTUAL_LY': [950_000]
        })

    query = sql.DEMO_KPI_QUERY + f" WHERE {where_sql}"
    return session.sql(query).to_pandas()
