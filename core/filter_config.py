"""
Filter Configuration

Defines available filters and their properties.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FilterConfig:
    """Configuration for a single filter."""

    filter_id: str              # Unique identifier (e.g., "region")
    label: str                  # Display label (e.g., "Region")
    session_key: str            # Session state key (e.g., "filter_region")
    sql_column: str             # SQL column name (e.g., "region_name")
    options: List[str]          # Available options
    default_label: str = "All"  # Default selection label


# ==========================================
# FILTER DEFINITIONS
# ==========================================

FILTER_CONFIGS = {
    "region": FilterConfig(
        filter_id="region",
        label="Region",
        session_key="filter_region",
        sql_column="region_name",
        options=["Americas", "EMEA", "APAC"],
        default_label="All Regions"
    ),
    "segment": FilterConfig(
        filter_id="segment",
        label="Segment",
        session_key="filter_segment",
        sql_column="segment_name",
        options=["Enterprise", "Mid-Market", "SMB"],
        default_label="All Segments"
    ),
}
