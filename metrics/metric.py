from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ui.components.donut_card_config import DonutCardConfig
    from ui.components.drill_config import DrillConfig


@dataclass(frozen=True)
class Metric:
    """
    Metric definition.

    This is the core dataclass that holds all configuration for a metric.
    Components look up metrics by key and read their config.
    """
    key: str
    title: str
    help_text: Optional[str] = None

    show_yoy: bool = True
    show_pacing_target: bool = True

    # Component-specific configs (optional slots)
    donut_config: Optional[DonutCardConfig] = None
    drill_config: Optional[DrillConfig] = None

    # Domain-specific WHERE clause filter (appended to SessionManager filters)
    extra_where: Optional[str] = None
