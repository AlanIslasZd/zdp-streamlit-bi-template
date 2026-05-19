"""Breakdown drill tab — self-contained, registry-driven component."""
import streamlit as st
import pandas as pd
import altair as alt

from metrics import get_validated
from services import snowflake_svc
from ui.components.formatters import FormatType, format_value
from core.config import CACTUS, YELLOW, RED


def render_breakdown_tab(metric_key: str, modal_where_sql: str) -> None:
    """
    Render the breakdown-by-dimension drill tab for a registered metric.

    Args:
        metric_key: Registered metric key (must have drill_config.breakdown_config).
        modal_where_sql: WHERE clause from the modal orchestrator.
    """
    metric = get_validated(metric_key, ["drill_config"])
    config = metric.drill_config.breakdown_config
    filter_map = config.filter_map
    format_type = config.format_type

    st.markdown("### Breakdown by Dimension")

    # Color legend (only show if metric has a target)
    has_target = metric.donut_config.target_qtd_col is not None
    if has_target:
        legend_html = f"""
        <div style='display: flex; gap: 20px; margin-bottom: 15px; padding: 10px; background-color: #0E1117; border-radius: 5px;'>
            <div style='display: flex; align-items: center; gap: 5px;'>
                <div style='width: 16px; height: 16px; background-color: {CACTUS}; border-radius: 3px;'></div>
                <span style='font-size: 13px; color: #FAFAFA;'>≥100% (Green)</span>
            </div>
            <div style='display: flex; align-items: center; gap: 5px;'>
                <div style='width: 16px; height: 16px; background-color: {YELLOW}; border-radius: 3px;'></div>
                <span style='font-size: 13px; color: #FAFAFA;'>95-100% (Yellow)</span>
            </div>
            <div style='display: flex; align-items: center; gap: 5px;'>
                <div style='width: 16px; height: 16px; background-color: {RED}; border-radius: 3px;'></div>
                <span style='font-size: 13px; color: #FAFAFA;'>&lt;95% (Red)</span>
            </div>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)

    st.markdown("**Filters**")
    fc1, fc2, fc3 = st.columns(3)

    # Column 1: Select dimension to break down by
    dim_options = list(filter_map.keys())
    with fc1:
        selected_dim = st.selectbox(
            "Break down by:",
            options=dim_options,
            index=0,
            key=f"dim_{metric_key}",
        )

    # Column 2: Select dimension to filter by
    with fc2:
        filter_choice = st.selectbox(
            "Filter by:",
            options=["(none)"] + dim_options,
            key=f"fc_{metric_key}",
        )

    # Column 3: Select filter values (dynamically fetched)
    with fc3:
        d_fvals = []
        if filter_choice != "(none)":
            # Fetch distinct values dynamically from the selected filter dimension
            filter_dimension_sql = filter_map[filter_choice]

            # Query Snowflake to get all distinct values for this dimension
            try:
                filter_values_df = snowflake_svc.fetch_breakdown_data(
                    metric_key,
                    filter_dimension_sql,
                    modal_where_sql
                )
                available_values = sorted(filter_values_df["DIM_VALUE"].dropna().unique().tolist())
            except:
                # Fallback to empty list if query fails
                available_values = []

            d_fvals = st.multiselect(
                filter_choice,
                options=available_values,
                key=f"fv_{metric_key}",
            )

    # Build WHERE clause with additional filter
    extra_where = modal_where_sql
    if d_fvals and filter_choice != "(none)":
        filter_col = filter_map[filter_choice]
        fv = "','".join(d_fvals)
        extra_where += f" AND {filter_col} IN ('{fv}')"

    dimension_sql = filter_map.get(selected_dim, dim_options[0])

    st.markdown(f"**By {selected_dim}**")

    with st.spinner(f"Loading {selected_dim} breakdown..."):
        try:
            breakdown_df = snowflake_svc.fetch_breakdown_data(
                metric_key, dimension_sql, extra_where,  # Use extra_where with optional filter
            )
            _render_chart(breakdown_df, selected_dim, format_type)

            # === NEW: Click-to-Export Feature ===
            # Render export UI below the chart
            _render_slice_export_ui(
                df=breakdown_df,
                dimension_name=selected_dim,
                dimension_sql_col=dimension_sql,
                base_where_sql=extra_where,
                format_type=format_type
            )
        except Exception as e:
            st.error(f"Error loading breakdown: {e}")
            st.exception(e)


def _render_chart(df: pd.DataFrame, dimension_name: str, format_type: FormatType) -> None:
    """
    Render horizontal bar chart with optional attainment coloring.

    Handles metrics WITH targets (shows attainment colors) and WITHOUT targets (simple bars).
    This is the "Enterprise-grade" fix that decouples UI from data structure.
    """
    if df.empty:
        st.warning("No data available for this breakdown.")
        return

    # CRITICAL: Check if this metric actually has a target column
    # This makes the component resilient to "Has Target? NO" briefs
    has_target = "TARGET" in df.columns and pd.notnull(df["TARGET"]).any()

    # Format actual values for display
    df["ACTUAL_FMT"] = df["ACTUAL"].apply(lambda x: format_value(x, format_type))

    if has_target:
        # === SCENARIO A: Metric WITH target (e.g., Revenue with quota) ===
        # Calculate attainment and assign colors
        df["ATTAINMENT"] = df.apply(
            lambda row: row["ACTUAL"] / row["TARGET"] if pd.notnull(row.get("TARGET")) and row["TARGET"] > 0 else 0,
            axis=1
        )
        df["COLOR"] = df["ATTAINMENT"].apply(lambda x: CACTUS if x >= 1.0 else (YELLOW if x >= 0.95 else RED))
        df["TARGET_FMT"] = df["TARGET"].apply(lambda x: format_value(x, format_type))
        df["ATTAINMENT_FMT"] = df["ATTAINMENT"].apply(lambda x: f"{x * 100:.0f}%")

        # Create Altair chart with attainment coloring
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y("DIM_VALUE:N", sort="-x", title=dimension_name),
            x=alt.X("ACTUAL:Q", title="Actual"),
            color=alt.Color("COLOR:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("DIM_VALUE:N", title=dimension_name),
                alt.Tooltip("ACTUAL_FMT:N", title="Actual"),
                alt.Tooltip("TARGET_FMT:N", title="Target"),
                alt.Tooltip("ATTAINMENT_FMT:N", title="Attainment"),
            ]
        ).properties(
            height=max(300, len(df) * 30)
        )
    else:
        # === SCENARIO B: Metric WITHOUT target (e.g., Ticket Count) ===
        # Just render simple bars with a single color
        chart = alt.Chart(df).mark_bar(color=CACTUS).encode(
            y=alt.Y("DIM_VALUE:N", sort="-x", title=dimension_name),
            x=alt.X("ACTUAL:Q", title="Actual"),
            tooltip=[
                alt.Tooltip("DIM_VALUE:N", title=dimension_name),
                alt.Tooltip("ACTUAL_FMT:N", title="Actual"),
            ]
        ).properties(
            height=max(300, len(df) * 30)
        )

    st.altair_chart(chart, use_container_width=True)

    # Show data table
    with st.expander("📊 View Data Table"):
        if has_target:
            display_df = df[["DIM_VALUE", "ACTUAL_FMT", "TARGET_FMT", "ATTAINMENT_FMT"]].copy()
            display_df.columns = [dimension_name, "Actual", "Target", "Attainment"]
        else:
            display_df = df[["DIM_VALUE", "ACTUAL_FMT"]].copy()
            display_df.columns = [dimension_name, "Actual"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def _render_slice_export_ui(
    df: pd.DataFrame,
    dimension_name: str,
    dimension_sql_col: str,
    base_where_sql: str,
    format_type: FormatType
):
    """
    Render click-to-export UI for dimension slices.

    Users can expand any dimension value and export just those records.
    This is the "Enterprise" feature that works for any dashboard.

    Args:
        df: Breakdown data (DIM_VALUE, ACTUAL columns)
        dimension_name: "Working Region" (display name for UI)
        dimension_sql_col: "REGION_BUCKET" (actual SQL column name)
        base_where_sql: "HANDOFF_BUCKET = '0'" (existing filters from sidebar + modal)
        format_type: How to format numbers
    """
    # Wrap entire export section in expander (like "View Data Table")
    with st.expander("💾 Export by Slice"):
        st.caption("Click to export records for a specific dimension value")

        # Create export buttons for each dimension value
        for idx, row in df.iterrows():
            dim_value = row['DIM_VALUE']
            actual_count = int(row['ACTUAL'])

            # Use expander for each slice
            with st.expander(f"📊 {dim_value} ({actual_count:,} records)"):
                # Build WHERE clause for this specific slice
                slice_where = f"{base_where_sql} AND {dimension_sql_col} = '{dim_value}'"

                st.markdown(f"**Filters Applied:**")
                st.code(slice_where, language="sql")

                button_key = f"export_{dimension_sql_col}_{dim_value}_{idx}"
                if st.button(
                    f"📥 Export {actual_count:,} records",
                    key=button_key,
                    help=f"Download all records where {dimension_name} = {dim_value}"
                ):
                    with st.spinner(f"Fetching {actual_count:,} records..."):
                        # Import here to avoid circular dependency
                        from services.snowflake_svc.drill_down import fetch_raw_data_for_export

                        export_df = fetch_raw_data_for_export(slice_where)

                        # Convert to CSV
                        csv_data = export_df.to_csv(index=False)

                        # Success message
                        st.success(f"✅ Ready to download {len(export_df):,} records")

                        # Download button
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv_data,
                            file_name=f"export_{dimension_name.replace(' ', '_')}_{dim_value}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key=f"download_{button_key}"
                        )
