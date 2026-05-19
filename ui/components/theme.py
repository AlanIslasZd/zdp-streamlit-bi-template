"""Theme and Styling

Applies dark theme styling to the Streamlit app.
"""
import streamlit as st
from core.config import LICORICE, CARD_BG


def apply_dark_theme():
    """Apply dark theme with custom styling."""
    st.markdown(
        f"""
        <style>
        /* Global background */
        .stApp {{
            background-color: {LICORICE};
        }}

        /* Card backgrounds */
        .element-container {{
            background-color: {CARD_BG};
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {CARD_BG};
        }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background-color: {CARD_BG};
            padding: 1rem;
            border-radius: 0.5rem;
        }}

        /* Headers */
        h1, h2, h3 {{
            color: #ffffff;
        }}

        /* Remove padding */
        .block-container {{
            padding-top: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
