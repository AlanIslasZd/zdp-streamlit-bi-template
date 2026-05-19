# Troubleshooting Guide

Common issues and how to fix them.

---

## SQL Type Casting Issues

### Error: "Numeric value 'X+' is not recognized"

**Symptom:**
```
SnowparkSQLException: Numeric value '3+' is not recognized
```

**Cause:** CASE statement returns mixed types without explicit VARCHAR cast.

**Solution:**

❌ **Wrong:**
```sql
CASE
    WHEN value = 0 THEN '0'
    WHEN value >= 3 THEN '3+'
END AS bucket
```

✅ **Correct:**
```sql
CAST(
    CASE
        WHEN value = 0 THEN '0'
        WHEN value >= 3 THEN '3+'
        ELSE 'Unknown'
    END AS VARCHAR
) AS bucket
```

**Where to fix:**
1. Find CASE statement in `services/snowflake_svc/{service}/sql.py`
2. Wrap entire CASE statement with `CAST(...AS VARCHAR)`
3. Restart Streamlit app
4. Test filter again

**Prevention:** Test your SQL in Snow CLI before putting it in the brief. The brief template now includes a "SQL Correctness Contract" section that explains this is YOUR responsibility as the analyst.

---

### Error: "Filter not working (no error shown)"

**Symptom:** Filter widget appears, you select values, but KPI doesn't change.

**Cause:** Filter options in `core/filter_config.py` don't match actual data values.

**Solution:**

1. **Check actual data values:**
```bash
snow sql -q "SELECT DISTINCT {filter_column} FROM {table} WHERE {business_filter}"
```

2. **Compare to filter config:**
```python
# In core/filter_config.py
FilterConfig(
    options=["1 - Critical", "2 - Major"]  # ← Does this match data?
)
```

3. **Update options to EXACT match:**
```python
FilterConfig(
    options=["1 Critical", "2 Major"]  # ← Match spacing, capitalization
)
```

**Common mismatches:**
- Hyphens: "1 - Critical" vs "1 Critical"
- Spacing: "1Critical" vs "1 Critical"
- Capitalization: "amer" vs "AMER"
- Special chars: "3 plus" vs "3+"

**Prevention:** Always validate filter options with Snow CLI before generating dashboard. The brief template now includes a Filter Value Validation checklist (Section 3.1).

---

## Import Errors

### Error: `ModuleNotFoundError: No module named 'services'`

**Cause:** Python can't find the services module.

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/your-dashboard

# Try running from the root
python -c "import sys; sys.path.insert(0, '.'); from services import snowflake_svc"
```

### Error: `ImportError: cannot import name 'my_service'`

**Cause:** Service not properly exported.

**Solution:**
1. Check `services/snowflake_svc/__init__.py` exports your service:
   ```python
   from .my_service import fetch_my_kpi
   __all__ = ['fetch_my_kpi']
   ```

2. Check `services/snowflake_svc/my_service/__init__.py` exists and exports the function

---

## Metric Registry Errors

### Error: `KeyError: Metric 'my_metric' not registered`

**Cause:** Metric isn't registered before being used.

**Solution:**
1. Check metric is defined in `metrics/definitions/my_domain.py`
2. Check `metrics/loader.py` calls `my_domain.register_all()`
3. Check page calls `metric_registry.register_all()` at the top of `render()`

### Error: `TypeError: Metric 'my_metric' is missing required configs: ['donut_config']`

**Cause:** Component expects a config that wasn't provided.

**Solution:**
Add the missing config when registering:
```python
register(Metric(
    key="my_metric",
    donut_config=DonutCardConfig(...),  # ← Add this
))
```

---

## SQL / Snowflake Errors

### Error: `SQL compilation error: Object 'MY_TABLE' does not exist`

**Cause:** Table name is wrong or you don't have access.

**Solution:**
1. Test query directly:
   ```bash
   snow sql -q "SELECT * FROM MY_SCHEMA.MY_TABLE LIMIT 1"
   ```
2. Check table name spelling (case-sensitive!)
3. Verify you have SELECT permissions

### Error: `SQL compilation error: Invalid column name 'MY_COLUMN'`

**Cause:** Column doesn't exist or is misspelled.

**Solution:**
1. Check column name in dashboard brief matches actual table
2. See available columns:
   ```bash
   snow sql -q "SHOW COLUMNS IN MY_SCHEMA.MY_TABLE"
   ```
3. Remember: Snowflake column names are case-sensitive in quotes

### Error: Query returns empty DataFrame

**Cause:** Filters are too restrictive or date range is wrong.

**Solution:**
1. Test without filters:
   ```bash
   snow sql -q "SELECT COUNT(*) FROM MY_TABLE"
   ```
2. Check date logic (`CURRENT_DATE()` might be different than expected)
3. Verify business filters are correct

---

## Filter Issues

### Filters Don't Update the Dashboard

**Cause:** `where_sql` not properly connected to service function.

**Solution:**
1. Check page passes `where_sql` to `render_donut_card()`:
   ```python
   where_sql = render_filters(...)
   render_donut_card("my_metric", where_sql)  # ← Pass where_sql
   ```

2. Check service function uses `where_sql`:
   ```python
   def fetch_my_kpi(where_sql: str):
       query = MY_QUERY
       if where_sql != "1=1":
           query += f" AND {where_sql}"
   ```

### Filter Options Don't Appear

**Cause:** Filter not defined in `core/filter_config.py`.

**Solution:**
Add filter to FILTER_CONFIGS:
```python
FILTER_CONFIGS = {
    "my_filter": FilterConfig(
        filter_id="my_filter",
        label="My Filter",
        session_key="filter_my_filter",
        sql_column="MY_SQL_COLUMN",
        options=["Option1", "Option2"],
        default_label="All"
    ),
}
```

---

## Drill-Down Issues

### "Details" Button Doesn't Appear

**Cause:** Metric doesn't have `drill_config`.

**Solution:**
Add drill config when registering metric:
```python
register(Metric(
    key="my_metric",
    drill_config=DrillConfig(...),  # ← Add this
))
```

### Drill Modal Opens But Shows No Data

**Cause:** `BASE_CTE` in drill_down/sql.py doesn't match your table.

**Solution:**
Update `services/snowflake_svc/drill_down/sql.py`:
```python
BASE_CTE = """
WITH my_data AS (
    SELECT
        -- Your dimensions here
        dimension1,
        dimension2,
        -- Your metrics here
        COUNT(*) AS metric_value
    FROM MY_SCHEMA.MY_TABLE
    WHERE [your_filters]
)
"""
```

### Dimension Not in Dropdown

**Cause:** Dimension not added to `FILTER_MAP`.

**Solution:**
Add to `services/snowflake_svc/drill_down/sql.py`:
```python
FILTER_MAP = {
    "My Dimension": "MY_SQL_COLUMN",
}
```

---

## Display Issues

### Gauge Chart Doesn't Show (Expected One)

**Cause:** Target not configured.

**Solution:**
If you WANT a gauge, add target to metric config:
```python
donut_config=DonutCardConfig(
    actual_col="ACTUAL",
    target_qtd_col="TARGET",  # ← Add this
    thresholds={'green': 1.0, 'yellow': 0.95},  # ← Add this
)
```

### Gauge Shows But Shouldn't

**Cause:** Target configured when you don't want one.

**Solution:**
Remove target from config:
```python
donut_config=DonutCardConfig(
    actual_col="ACTUAL",
    target_qtd_col=None,  # ← No target
    thresholds=None,  # ← No thresholds
)
```

### Values Display as "$0.0M" When They Shouldn't

**Cause:** Wrong format type.

**Solution:**
Check `format_type` in metric config:
```python
# For ticket counts:
format_type=FormatType.NUMBER

# For revenue:
format_type=FormatType.CURRENCY

# For percentages:
format_type=FormatType.PERCENTAGE
```

---

## Streamlit Issues

### App Won't Start

**Cause:** Missing dependencies or syntax errors.

**Solution:**
1. Check for syntax errors:
   ```bash
   python -m py_compile streamlit_app.py
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Check error message in terminal

### App Crashes on Page Load

**Cause:** Exception in render() function.

**Solution:**
1. Check terminal for full error traceback
2. Common causes:
   - Metric not registered
   - SQL query fails
   - Missing column in DataFrame
3. Wrap render() in try-except to see error:
   ```python
   try:
       # Your code
   except Exception as e:
       st.error("Error!")
       st.exception(e)  # Shows full traceback
   ```

### Cache Not Clearing

**Cause:** Streamlit cache holds old data.

**Solution:**
```bash
# In terminal where Streamlit is running, press:
C  # Clear cache

# Or in code:
st.cache_data.clear()
```

---

## Mock Data Issues

### Mock Data Doesn't Match Real Data Structure

**Cause:** Mock DataFrame columns don't match what component expects.

**Solution:**
Make sure mock data has exact same columns as real query:
```python
if session is None:
    return pd.DataFrame({
        'ACTUAL_COL': [value],  # ← Match SQL column names exactly
        'TARGET_COL': [value],
    })
```

### App Stuck in Mock Mode

**Cause:** `USE_MOCK_DATA` still True.

**Solution:**
Edit `core/config.py`:
```python
USE_MOCK_DATA = False  # ← Change to False
```

---

## Performance Issues

### Dashboard Loads Slowly

**Cause:** Query is slow or not cached.

**Solution:**
1. Check service function has `@st.cache_data`:
   ```python
   @st.cache_data(ttl=3600)
   def fetch_my_kpi(where_sql: str):
   ```

2. Test query speed directly:
   ```bash
   time snow sql -q "YOUR_QUERY"
   ```

3. Optimize SQL (add indexes, reduce data scanned)

### Drill-Down Takes Forever to Load

**Cause:** Breakdown query is expensive.

**Solution:**
1. Add WHERE clause to limit data:
   ```sql
   WHERE CREATED_TIMESTAMP >= DATEADD('day', -30, CURRENT_DATE())
   ```

2. Pre-aggregate data in a view
3. Add LIMIT to query for testing

---

## Deployment Issues (SiS)

### Can't Find App in Snowflake

**Cause:** Not deployed correctly.

**Solution:**
1. Check you pushed to GitHub first
2. In Snowflake UI: Streamlit → Create → From GitHub
3. Select correct repo and branch

### App Works Locally But Not in SiS

**Cause:** Different environment.

**Solution:**
1. Check `USE_MOCK_DATA = False` in deployed version
2. Verify Snowflake connection name:
   ```python
   SNOWFLAKE_CONNECTION = "snowflake"  # Default for SiS
   ```

3. Check app has permissions to access tables

---

## Getting More Help

**Still stuck?**

1. **Check CLAUDE.md** - See architectural rules
2. **Review Example** - Look at `docs/DASHBOARD_BRIEF_EXAMPLE_Z2.md`
3. **Read Source Code** - Check `ui/components/donut_card.py` to understand how components work
4. **Ask in Slack** - #zdp-bi-team channel
5. **Check Logs** - Terminal output often shows the exact error

**When asking for help, include:**
- Error message (full traceback)
- What you tried
- Your dashboard brief
- Relevant code snippet

---

## Prevention Tips

**Avoid issues by:**
- ✅ Testing SQL with Snow CLI FIRST
- ✅ Using exact column names from brief
- ✅ Following the template structure
- ✅ Starting with mock data
- ✅ Adding metrics one at a time
- ✅ Checking imports after each change

**Remember:** Most issues come from mismatches between the brief and the actual code. When in doubt, check your brief!
