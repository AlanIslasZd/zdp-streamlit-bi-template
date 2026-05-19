from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ui.components.drill_tabs.breakdown_config import BreakdownTabConfig
    from ui.components.drill_tabs.trend_config import TrendTabConfig


@dataclass(frozen=True)
class DrillConfig:
    """
    Configuration for drill-down modal.

    Defines which tabs are available and their configuration.
    """
    drill_key: str                                          # Unique button identifier
    drill_title: str                                        # Modal header title
    tabs: List[str]                                         # Enabled tabs (e.g., ["breakdown", "trend"])
    modal_filters: List[str]                                # Additional filters in modal
    breakdown_config: Optional[BreakdownTabConfig] = None   # Config for breakdown tab
    trend_config: Optional[TrendTabConfig] = None           # Config for trend tab
