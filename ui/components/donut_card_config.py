from dataclasses import dataclass
from typing import Callable, Dict, Optional

import pandas as pd

from ui.components.formatters import FormatType, YoYFormat


@dataclass(frozen=True)
class DonutCardConfig:
    """
    Configuration for DonutCard component.

    This config tells the donut card:
    - Which service function to call
    - Which columns to extract from the DataFrame
    - How to format and display values
    """
    # Required fields (no defaults) — must come first
    service_fn: Callable[[str], pd.DataFrame]
    actual_col: str
    format_type: FormatType

    # Optional fields (with defaults)
    target_qtd_col: Optional[str] = None
    thresholds: Optional[Dict[str, float]] = None
    invert_target: bool = False
    yoy_actual_col: Optional[str] = None
    yoy_ly_col: Optional[str] = None
    yoy_delta_col: Optional[str] = None
    yoy_format: YoYFormat = YoYFormat.PCT_CHANGE

    def __post_init__(self):
        """Validate YoY configuration."""
        has_pair = self.yoy_actual_col is not None and self.yoy_ly_col is not None
        has_delta = self.yoy_delta_col is not None
        sources = sum([has_pair, has_delta])
        if sources > 1:
            raise ValueError(
                "DonutCardConfig: provide at most one YoY source — "
                "(yoy_actual_col + yoy_ly_col) or yoy_delta_col."
            )
