"""BreakdownTabConfig — declarative config for the breakdown drill tab."""
from __future__ import annotations

from dataclasses import dataclass

from ui.components.formatters import FormatType


@dataclass(frozen=True)
class BreakdownTabConfig:
    """
    Configuration for the Breakdown tab inside a drill modal.

    Args:
        filter_map: Dimension display name → SQL column expression mapping.
        format_type: How chart values are formatted (currency, count, percentage).
    """

    filter_map: dict
    format_type: FormatType
