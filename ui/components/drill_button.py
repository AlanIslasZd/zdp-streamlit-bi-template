"""Drill-Down Button Component

Standardized button wrapper that opens drill-down modal dialogs.
"""
import streamlit as st


def render_drill_button(
    key: str,
    label: str = "Details",
    help_text: str = None
) -> bool:
    """
    Render standardized drill-down button.

    Args:
        key: Unique button key
        label: Button text (default: "Details")
        help_text: Optional tooltip text

    Returns:
        True if button was clicked, False otherwise
    """
    return st.button(
        label,
        key=key,
        type="secondary",
        help=help_text,
        use_container_width=False
    )
