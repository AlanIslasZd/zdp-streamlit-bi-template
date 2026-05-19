"""Trend Tab Configuration

Configuration for metric trend analysis in drill-down modals.
"""
from dataclasses import dataclass
from typing import Literal
from ui.components.formatters import FormatType


@dataclass
class TrendTabConfig:
    """
    Configuration for trend tab rendering.

    Attributes:
        date_column: SQL column name for the X-axis (e.g., "CREATED_TIMESTAMP")
        default_granularity: Default time bucket ("Daily", "Weekly", "Monthly")
        format_type: How to format Y-axis and tooltips (from metric's donut_config)
    """
    date_column: str
    default_granularity: Literal["Daily", "Weekly", "Monthly"] = "Daily"
    format_type: FormatType = FormatType.CURRENCY
