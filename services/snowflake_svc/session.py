"""
Snowflake Session Management

Centralized Snowflake connection handling with mock data fallback.
"""
import os
import streamlit as st
from core import config


@st.cache_resource
def get_snowflake_session():
    """
    Get Snowflake session with caching.

    Returns:
        Snowpark Session if USE_MOCK_DATA=False, None otherwise
    """
    if config.USE_MOCK_DATA:
        st.warning("📊 Running in MOCK DATA mode. Set environment variable `USE_MOCK_DATA=False` or edit `core/config.py` to connect to Snowflake.")
        return None

    # Try Streamlit in Snowflake session first (production)
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except:
        pass  # Not in SiS, try local connection

    # Try local connection with credentials (for local development)
    try:
        from snowflake.snowpark import Session

        # Read credentials from Streamlit secrets
        if "snowflake" in st.secrets:
            connection_parameters = {
                "account": st.secrets.snowflake.account,
                "user": st.secrets.snowflake.user,
                "role": st.secrets.snowflake.get("role", "SYSADMIN"),
                "warehouse": st.secrets.snowflake.get("warehouse", "COMPUTE_WH"),
                "database": st.secrets.snowflake.get("database", "FUNCTIONAL"),
                "schema": st.secrets.snowflake.get("schema", "CUSTOMER_EXPERIENCE"),
            }

            # Add authentication method
            if "authenticator" in st.secrets.snowflake:
                connection_parameters["authenticator"] = st.secrets.snowflake.authenticator
            elif "password" in st.secrets.snowflake:
                connection_parameters["password"] = st.secrets.snowflake.password
            else:
                st.warning("⚠️ No authentication method found. Add 'password' or 'authenticator' to secrets.toml")
                return None

            return Session.builder.configs(connection_parameters).create()
        else:
            # No st.secrets found, try Snow CLI config (fallback 2)
            pass

    except Exception as e:
        st.info(f"💡 Streamlit secrets connection failed: {e}")

    # Fallback 2: Try Snow CLI config (silent connection)
    try:
        import toml
        snow_config_path = os.path.expanduser("~/.snowflake/connections.toml")
        if os.path.exists(snow_config_path):
            snow_config = toml.load(snow_config_path)
            if "Global" in snow_config:
                # Silent connection - no st.info() message
                from snowflake.snowpark import Session
                connection_parameters = {
                    "account": snow_config["Global"]["account"],
                    "user": snow_config["Global"]["user"],
                    "authenticator": snow_config["Global"].get("authenticator", "externalbrowser"),
                    "warehouse": snow_config["Global"].get("warehouse", "COMPUTE_WH"),
                    "role": snow_config["Global"].get("role", "SYSADMIN"),
                    "database": snow_config["Global"].get("database", "FUNCTIONAL"),
                    "schema": snow_config["Global"].get("schema", "CUSTOMER_EXPERIENCE"),
                }
                return Session.builder.configs(connection_parameters).create()
    except Exception as e:
        # Silent failure - connection errors will be caught by mock data fallback
        pass

    # Final fallback: mock data with clear instructions
    st.warning("⚠️ USING MOCK DATA - No Snowflake connection found")
    st.info("""
**To connect to real Snowflake, choose ONE:**
1. Add credentials to `.streamlit/secrets.toml`
2. Configure Snow CLI: `snow connection add`
3. Deploy to Streamlit in Snowflake (auto-detects)
""")
    return None
