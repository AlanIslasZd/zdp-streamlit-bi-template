"""
Configuration Constants

All configuration values for the application.
Use UPPERCASE naming for constants.
"""
import os

# ==========================================
# CONNECTION SETTINGS
# ==========================================

# Mock data mode - supports environment variable override
# Usage:
#   - CLI: USE_MOCK_DATA=True streamlit run streamlit_app.py
#   - Code: Change default below to True for local dev
#   - Production: Defaults to False (real Snowflake data)
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'False').lower() in ('true', '1', 'yes')

SNOWFLAKE_CONNECTION = "snowflake"  # Connection name in Snowflake (default for SiS)

# ==========================================
# UI COLORS
# ==========================================

LICORICE = "#1f1f1f"  # Dark background
CACTUS = "#5e6e5a"    # Muted green
CARD_BG = "#2d2d2d"   # Card background
RED = "#e74c3c"       # Alert/below threshold
YELLOW = "#f39c12"    # Warning/approaching threshold
GREEN = "#2ecc71"     # Success/above threshold

# ==========================================
# THRESHOLDS
# ==========================================

DEFAULT_THRESHOLDS = {
    'green': 1.0,   # ≥100% attainment
    'yellow': 0.95,  # ≥95% attainment
    'red': 0.0       # <95% attainment
}
