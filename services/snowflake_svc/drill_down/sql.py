"""Drill-Down SQL Queries"""

# Maps UI dimension names to SQL column names
FILTER_MAP = {
    "Region": "region_name",
    "Segment": "segment_name",
    "Leader Team": "leader_team",
}

BASE_CTE = """
WITH demo_data AS (
    SELECT
        region_name,
        segment_name,
        leader_team,
        metric_value,
        target_value,
        booking_date
    FROM demo_schema.demo_metrics_table
)
"""

# Parameterized breakdown query (dimension_sql injected at runtime)
BREAKDOWN_QUERY_TEMPLATE = BASE_CTE + """
SELECT
    {dimension_sql} AS DIM_VALUE,
    SUM(metric_value) AS ACTUAL,
    SUM(target_value) AS TARGET
FROM demo_data
WHERE {where_sql}
GROUP BY DIM_VALUE
ORDER BY ACTUAL DESC
"""

# Parameterized trend query (date_col and date_trunc injected at runtime)
TREND_QUERY_TEMPLATE = BASE_CTE + """
SELECT
    DATE_TRUNC('{date_trunc}', {date_col}) AS PERIOD,
    TO_CHAR(DATE_TRUNC('{date_trunc}', {date_col}), '{label_format}') AS LBL,
    SUM(metric_value) AS VALUE
FROM demo_data
WHERE {where_sql}
GROUP BY PERIOD, LBL
ORDER BY PERIOD ASC
"""
