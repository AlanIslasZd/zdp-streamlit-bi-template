"""Drill-Down Service Functions"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from . import sql
from ..session import get_snowflake_session


def _generate_mock_breakdown_data(dimension_sql: str, where_sql: str) -> pd.DataFrame:
    """
    Generate realistic mock data based on dimension and filters.

    This simulates what real Snowflake data would return.
    """
    # Define mock data for each dimension
    mock_data_by_dimension = {
        "region_name": [
            {"DIM_VALUE": "Americas", "ACTUAL": 600_000, "TARGET": 550_000},
            {"DIM_VALUE": "EMEA", "ACTUAL": 400_000, "TARGET": 420_000},
            {"DIM_VALUE": "APAC", "ACTUAL": 250_000, "TARGET": 230_000},
        ],
        "segment_name": [
            {"DIM_VALUE": "Enterprise", "ACTUAL": 700_000, "TARGET": 650_000},
            {"DIM_VALUE": "Mid-Market", "ACTUAL": 400_000, "TARGET": 400_000},
            {"DIM_VALUE": "SMB", "ACTUAL": 150_000, "TARGET": 150_000},
        ],
        "leader_team": [
            {"DIM_VALUE": "Team A", "ACTUAL": 450_000, "TARGET": 400_000},
            {"DIM_VALUE": "Team B", "ACTUAL": 400_000, "TARGET": 420_000},
            {"DIM_VALUE": "Team C", "ACTUAL": 400_000, "TARGET": 380_000},
        ],
    }

    # Get data for selected dimension (default to region)
    data = mock_data_by_dimension.get(dimension_sql, mock_data_by_dimension["region_name"])
    df = pd.DataFrame(data)

    # Simulate filtering based on where_sql
    # In mock mode, we'll just return all data (real Snowflake would apply WHERE clause)
    # But if filters contain specific values, we could filter the mock data here

    # For demo purposes: if segment filter applied, reduce the data proportionally
    if "segment_name IN ('Enterprise')" in where_sql:
        # Simulate filtering to just Enterprise segment
        df["ACTUAL"] = df["ACTUAL"] * 0.6  # Enterprise is ~60% of revenue
        df["TARGET"] = df["TARGET"] * 0.6
    elif "segment_name IN ('Mid-Market')" in where_sql:
        df["ACTUAL"] = df["ACTUAL"] * 0.3  # Mid-Market is ~30% of revenue
        df["TARGET"] = df["TARGET"] * 0.3
    elif "segment_name IN ('SMB')" in where_sql:
        df["ACTUAL"] = df["ACTUAL"] * 0.1  # SMB is ~10% of revenue
        df["TARGET"] = df["TARGET"] * 0.1

    return df


def _generate_mock_trend_data(granularity: str) -> pd.DataFrame:
    """
    Generate realistic time-series mock data.

    Returns DataFrame with PERIOD, LBL, VALUE columns.
    """
    today = datetime.now()

    # Determine number of periods and delta based on granularity
    if granularity == "Daily":
        periods = 30
        delta = timedelta(days=1)
        label_format = "%b %d"
    elif granularity == "Weekly":
        periods = 12
        delta = timedelta(weeks=1)
        label_format = "%b %d"
    else:  # Monthly
        periods = 12
        delta = timedelta(days=30)
        label_format = "%b %Y"

    # Generate time-series data with slight growth trend
    data = []
    base_value = 500_000

    for i in range(periods):
        period_date = today - (periods - i - 1) * delta
        # Add growth trend + some randomness
        value = base_value * (1 + i * 0.02) * (0.9 + (i % 3) * 0.1)

        data.append({
            "PERIOD": period_date,
            "LBL": period_date.strftime(label_format),
            "VALUE": value
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def fetch_breakdown_data(
    metric_key: str,
    dimension_sql: str,
    where_sql: str
) -> pd.DataFrame:
    """
    Fetch breakdown data by a single dimension.

    Args:
        metric_key: Metric identifier (not used in demo, kept for compatibility)
        dimension_sql: SQL column name for grouping dimension
        where_sql: WHERE clause from SessionManager

    Returns:
        DataFrame with columns: DIM_VALUE, ACTUAL, TARGET
    """
    session = get_snowflake_session()

    # Mock data for local development
    if session is None:
        return _generate_mock_breakdown_data(dimension_sql, where_sql)

    query = sql.BREAKDOWN_QUERY_TEMPLATE.format(
        dimension_sql=dimension_sql,
        where_sql=where_sql
    )
    return session.sql(query).to_pandas()


@st.cache_data(ttl=3600)
def fetch_trend_data(
    where_sql: str,
    date_col: str,
    granularity: str
) -> pd.DataFrame:
    """
    Fetch time-series trend data.

    Args:
        where_sql: WHERE clause from SessionManager
        date_col: SQL column name for time dimension (e.g., "CREATED_TIMESTAMP")
        granularity: Time bucket ("Daily", "Weekly", "Monthly")

    Returns:
        DataFrame with columns: PERIOD (datetime), LBL (str), VALUE (numeric)
    """
    session = get_snowflake_session()

    # Mock data for local development
    if session is None:
        return _generate_mock_trend_data(granularity)

    # Map granularity to Snowflake DATE_TRUNC units
    date_trunc_map = {
        "Daily": "DAY",
        "Weekly": "WEEK",
        "Monthly": "MONTH"
    }

    # Map granularity to label formats
    label_format_map = {
        "Daily": "Mon DD",
        "Weekly": "Mon DD",
        "Monthly": "Mon YYYY"
    }

    date_trunc = date_trunc_map.get(granularity, "DAY")
    label_format = label_format_map.get(granularity, "Mon DD")

    query = sql.TREND_QUERY_TEMPLATE.format(
        date_col=date_col,
        date_trunc=date_trunc,
        label_format=label_format,
        where_sql=where_sql
    )

    return session.sql(query).to_pandas()


@st.cache_data(ttl=3600)
def fetch_raw_data_for_export(
    where_sql: str,
    row_limit: int = 100000
) -> pd.DataFrame:
    """
    Fetch raw data for CSV export (click-to-export feature).

    This uses the SAME BASE_CTE as breakdown queries to ensure
    consistency between what users see in charts and what they export.

    Args:
        where_sql: Combined filter clause (sidebar + modal + slice)
                  e.g., "HANDOFF_BUCKET = '0' AND REGION_BUCKET = 'AMER'"
        row_limit: Maximum rows to export (safety limit)

    Returns:
        DataFrame with all columns from BASE_CTE
    """
    session = get_snowflake_session()

    # Mock data for local development
    if session is None:
        # Generate mock data
        import numpy as np
        num_rows = min(100, row_limit)  # Generate 100 sample rows

        return pd.DataFrame({
            'id': range(1, num_rows + 1),
            'region_name': np.random.choice(['Americas', 'EMEA', 'APAC'], num_rows),
            'segment_name': np.random.choice(['Enterprise', 'Mid-Market', 'SMB'], num_rows),
            'leader_team': np.random.choice(['Team A', 'Team B', 'Team C'], num_rows),
            'metric_value': np.random.uniform(10000, 50000, num_rows),
            'booking_date': pd.date_range('2024-01-01', periods=num_rows, freq='D'),
        })

    # Real Snowflake query: Use BASE_CTE to get all columns
    # Extract the CTE name from BASE_CTE (e.g., "demo_data")
    # This assumes BASE_CTE has format: "WITH cte_name AS (...)"
    query = sql.BASE_CTE + """
    SELECT *
    FROM demo_data
    WHERE {where_sql}
    LIMIT {row_limit}
    """.format(where_sql=where_sql, row_limit=row_limit)

    return session.sql(query).to_pandas()
