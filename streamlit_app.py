"""
Streamlit Enterprise Metrics Template
Entry point for the application
"""
import streamlit as st
from core.session import SessionManager
from ui.components.theme import apply_dark_theme
from ui.pages import demo

# Page configuration
st.set_page_config(
    page_title="Metrics Template",
    page_icon="📊",
    layout="wide"
)

# Apply dark theme
apply_dark_theme()

# Initialize session state
SessionManager.initialize()

# Navigation
page_demo = st.Page(
    demo.render,
    title="Demo Dashboard",
    icon="📊",
    url_path="demo"
)

pg = st.navigation([page_demo])
pg.run()
