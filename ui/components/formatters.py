"""Formatting Utilities

Provides utility functions for formatting numbers, percentages, and status colors.
"""
from enum import Enum
import pandas as pd
from core.config import CACTUS, YELLOW, RED


class FormatType(str, Enum):
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    NUMBER = "number"


class YoYFormat(str, Enum):
    PCT_CHANGE = "pct_change"
    PP_DELTA = "pp_delta"
    ABSOLUTE = "absolute"


def format_m(num) -> str:
    """
    Format number in millions with one decimal place and dollar sign.

    Args:
        num: Numeric value to format

    Returns:
        Formatted string (e.g., "$45.0M", "$120.5M")
    """
    if pd.isna(num) or num is None or num == 0:
        return "$0.0M"
    return f"${num / 1000000:.1f}M"


def format_pct(num) -> str:
    """
    Format decimal as percentage without decimal places.

    Args:
        num: Decimal value (0.0-1.0 range)

    Returns:
        Formatted string (e.g., "75%", "100%")
    """
    if pd.isna(num) or num is None:
        return "0%"
    return f"{num * 100:.0f}%"


def format_count(num) -> str:
    """
    Format count with thousands separator.

    Args:
        num: Numeric value

    Returns:
        Formatted string (e.g., "1,234", "45,678")
    """
    if pd.isna(num) or num is None or num == 0:
        return "0"
    return f"{int(num):,}"


# Formatter Aliases (for trend_tab.py compatibility)
def format_currency(num) -> str:
    """Alias for format_m (currency formatting)."""
    return format_m(num)


def format_number(num) -> str:
    """Alias for format_count (number formatting)."""
    return format_count(num)


def format_percentage(num) -> str:
    """Alias for format_pct (percentage formatting)."""
    return format_pct(num)


def format_value(value, format_type: FormatType) -> str:
    """
    Format a value based on type.

    Args:
        value: Numeric value to format
        format_type: Type of formatting to apply

    Returns:
        Formatted string
    """
    if format_type == FormatType.CURRENCY:
        return format_m(value)
    elif format_type == FormatType.PERCENTAGE:
        return format_pct(value)
    elif format_type == FormatType.NUMBER:
        return format_count(value)
    return str(value)


def format_delta(delta, yoy_format: YoYFormat = YoYFormat.PCT_CHANGE) -> str:
    """
    Format a delta/change value.

    Args:
        delta: Change value
        yoy_format: Format type for the delta

    Returns:
        Formatted string with +/- prefix
    """
    if pd.isna(delta) or delta is None:
        return "N/A"

    if yoy_format == YoYFormat.PCT_CHANGE:
        sign = "+" if delta >= 0 else ""
        return f"{sign}{delta * 100:.0f}%"
    elif yoy_format == YoYFormat.PP_DELTA:
        sign = "+" if delta >= 0 else ""
        return f"{sign}{delta * 100:.0f}pp"
    elif yoy_format == YoYFormat.ABSOLUTE:
        return format_m(delta)

    return str(delta)


def get_attainment_color(attainment: float, thresholds: dict) -> str:
    """
    Get color based on attainment and thresholds.

    Args:
        attainment: Attainment ratio (e.g., 1.05 = 105%)
        thresholds: Dict with 'green', 'yellow', 'red' threshold values

    Returns:
        Color hex code
    """
    if attainment >= thresholds.get('green', 1.0):
        return CACTUS
    elif attainment >= thresholds.get('yellow', 0.95):
        return YELLOW
    else:
        return RED
