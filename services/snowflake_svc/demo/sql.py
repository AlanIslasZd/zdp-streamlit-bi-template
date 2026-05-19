"""Demo Service SQL Queries"""

BASE_CTE = """
WITH demo_data AS (
    SELECT
        region_name,
        segment_name,
        fiscal_quarter,
        metric_value,
        target_value,
        ly_metric_value
    FROM demo_schema.demo_metrics_table
)
"""

DEMO_KPI_QUERY = BASE_CTE + """
SELECT
    SUM(metric_value) AS METRIC_VALUE,
    SUM(target_value) AS TARGET,
    SUM(ly_metric_value) AS ACTUAL_LY
FROM demo_data
"""
