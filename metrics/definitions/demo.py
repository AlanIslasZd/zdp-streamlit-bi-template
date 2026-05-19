"""Demo Metric Definitions"""
from metrics.metric import Metric
from metrics.registry import register
from ui.components.donut_card_config import DonutCardConfig
from ui.components.drill_config import DrillConfig
from ui.components.drill_tabs.breakdown_config import BreakdownTabConfig
from ui.components.drill_tabs.trend_config import TrendTabConfig
from ui.components.formatters import FormatType
from services import snowflake_svc
from services.snowflake_svc.drill_down.sql import FILTER_MAP


def register_all():
    """Register all demo metrics."""

    # Configure breakdown tab for drill-down
    _DEMO_BREAKDOWN = BreakdownTabConfig(
        filter_map=FILTER_MAP,
        format_type=FormatType.CURRENCY,
    )

    # Configure trend tab for time-series analysis
    _DEMO_TREND = TrendTabConfig(
        date_column="BOOKING_DATE",
        default_granularity="Daily",
        format_type=FormatType.CURRENCY,  # Must match donut_config format_type
    )

    register(Metric(
        key="demo_revenue",
        title="Demo Revenue",
        help_text="Example KPI showing revenue with YoY comparison, target pacing, and drill-down by dimension",
        donut_config=DonutCardConfig(
            service_fn=snowflake_svc.fetch_demo_kpi,
            actual_col="METRIC_VALUE",
            target_qtd_col="TARGET",
            format_type=FormatType.CURRENCY,
            thresholds={'green': 1.0, 'yellow': 0.95},
            yoy_actual_col="METRIC_VALUE",
            yoy_ly_col="ACTUAL_LY",
        ),
        drill_config=DrillConfig(
            drill_key="drill_demo_revenue",
            drill_title="Demo Revenue Breakdown",
            tabs=["breakdown", "trend"],  # Both breakdown and trend tabs
            modal_filters=[],    # No additional filters in modal
            breakdown_config=_DEMO_BREAKDOWN,
            trend_config=_DEMO_TREND,
        ),
        show_yoy=True,
        show_pacing_target=True,
    ))
