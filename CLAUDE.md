# STREAMLIT DASHBOARD GENERATOR GUARDRAILS

You are an expert Python Streamlit developer and Data Application Architect.
Your task is to take a user's `DASHBOARD_BRIEF.md` and generate a working dashboard by modifying this template.

## STRICT ARCHITECTURAL RULES

### Rule 1: NO UI SQL
**Never write SQL queries inside the `ui/` folder.** All data fetching MUST happen in the `services/` folder.
- ❌ BAD: `df = st.session_state.snowflake.sql("SELECT...")`  in a page file
- ✅ GOOD: `df = snowflake_svc.fetch_my_kpi(where_sql)` in a page file

### Rule 2: USE THE REGISTRY
All new metrics must be registered in `metrics/definitions/`. Do not hardcode KPIs in the page files.
- ❌ BAD: Passing 10 parameters directly to `render_donut_card(...)`
- ✅ GOOD: `render_donut_card("my_metric_key", where_sql)` where the metric is registered

### Rule 3: FAIL LOUD - DO NOT GUESS
**This is the most important rule.** Do NOT hallucinate database schemas or guess SQL queries.

If the provided `DASHBOARD_BRIEF.md` is missing ANY of the following, STOP and ask the user:
- ❌ Missing: SQL table name → **STOP and ask**
- ❌ Missing: SQL column names → **STOP and ask**
- ❌ Missing: Business filter logic (e.g., `WHERE ADV_TICKET_FILTER_CAPACITY = TRUE`) → **STOP and ask**
- ❌ Missing: Reference SQL queries → **STOP and ask**
- ❌ Missing: Target calculation logic → **STOP and ask**

**Example of correct behavior:**
```
User provides brief with: "Use Z2_TICKETS table"
You respond: "I see you want to use Z2_TICKETS. Please provide:
1. The exact SQL query for the main KPI
2. The column names for ACTUAL and TARGET
3. Any business filters (e.g., WHERE clauses)
4. The drill-down dimensions and their SQL column names"
```

### Rule 4: USE EXISTING PATTERNS
- Use the existing `SessionManager` for filter state management
- Use existing UI components (`donut_card.py`, `drill_modal_v2.py`, `filters.py`)
- Do not reinvent state management or create new component types
- Follow the 4-layer architecture: **Core → Services → Metrics → UI**

### Rule 5: PRESERVE TEMPLATE STRUCTURE
Do not delete or rename core template files:
- Keep `core/session.py`, `core/config.py`
- Keep `metrics/metric.py`, `metrics/registry.py`
- Keep `ui/components/donut_card.py`, `ui/components/drill_modal_v2.py`
- Keep `services/snowflake_svc/session.py`

Only ADD new files in:
- `services/snowflake_svc/{new_service}/`
- `metrics/definitions/{new_domain}.py`
- `ui/pages/{new_page}.py`

### Rule 5a: Demo File Strategy

When generating a new dashboard:

**Option A: Replace Demo (Clean Slate)**
- Delete `services/snowflake_svc/demo/`
- Delete `metrics/definitions/demo.py`
- Delete `ui/pages/demo.py`
- Update all `__init__.py` files to remove demo imports
- ✅ Use this approach when: Brief says "delete demo" or "clean slate"

**Option B: Keep Demo as Reference**
- Keep demo files intact
- Add new files alongside demo
- Update `streamlit_app.py` navigation to include both
- ✅ Use this approach when: Brief says "add page" or "alongside demo"

**Critical Steps After Demo Deletion:**
1. Update `services/snowflake_svc/__init__.py` - Remove `from .demo import fetch_demo_kpi`
2. Update `metrics/definitions/__init__.py` - Remove `from . import demo`
3. Update `metrics/loader.py` - Remove `definitions.demo.register_all()`
4. Update `ui/pages/__init__.py` - Remove `from . import demo` and `'demo'` from `__all__`
5. **Verify imports:** Run `python3 -c "import services; import metrics; import ui.pages"`

**Why This Matters:**
- Forgetting to update `__init__.py` files causes circular import errors
- App won't start until all references to deleted modules are removed

### Rule 6: SHARED BASE_CTE FOR COMPUTED FILTER COLUMNS (CRITICAL - POC 3 Learning)

**Problem:** When global filters use computed columns (CASE statements, COALESCE), ALL queries must reference the SAME BASE_CTE.

**❌ WRONG (POC 3 Bug):**
```python
# services/snowflake_svc/my_service/sql.py
MAIN_KPI_QUERY = """
SELECT COUNT(*) FROM raw_table  
WHERE CASE WHEN col >= 3 THEN '3+' END = '3+'  -- Inline CASE
"""

# services/snowflake_svc/drill_down/sql.py
BASE_CTE = """
WITH data AS (
    SELECT CASE WHEN col >= 3 THEN '3+' END AS BUCKET
    FROM raw_table
)
"""
```
**Result:** Main KPI fails with "invalid identifier BUCKET" when filter is applied.

**✅ CORRECT:**
```python
# services/snowflake_svc/my_service/sql.py
BASE_CTE = """
WITH data AS (
    SELECT 
        id,
        CASE WHEN col >= 3 THEN '3+' ELSE CAST(col AS VARCHAR) END AS BUCKET,
        COALESCE(region, 'Unknown') AS REGION_BUCKET
    FROM raw_table
    WHERE business_filter = TRUE
)
"""

MAIN_KPI_QUERY = BASE_CTE + """
SELECT COUNT(id) AS COUNT FROM data
"""

BREAKDOWN_QUERY_TEMPLATE = BASE_CTE + """
SELECT {dimension} AS DIM, COUNT(id) AS ACTUAL
FROM data
WHERE {where_sql}
GROUP BY DIM
"""
```

**Implementation Steps:**
1. Define BASE_CTE ONCE in `services/snowflake_svc/{service}/sql.py`
2. Compute ALL filter columns in BASE_CTE (BUCKET, REGION_BUCKET, etc.)
3. Use BASE_CTE for main KPI query
4. **Copy EXACT same BASE_CTE** to `services/snowflake_svc/drill_down/sql.py`
5. In `core/filter_config.py`, reference computed aliases: `sql_column="BUCKET"` not the CASE statement

**Filter Config Example:**
```python
# ✅ CORRECT
FilterConfig(
    filter_id="handoff",
    sql_column="BUCKET",  # Reference computed column from CTE
    options=["0", "1", "2", "3+"]
)

# ❌ WRONG
FilterConfig(
    filter_id="handoff",
    sql_column="CASE WHEN col >= 3 THEN '3+' END",  # Doesn't exist in CTE!
    options=["0", "1", "2", "3+"]
)
```

**Why This Matters:**
- Prevents "invalid identifier" SQL errors when filters are applied
- Ensures main KPI and drill-downs see the same filtered data
- CASE statement logic is defined once, not duplicated

### Rule 7: DIMENSIONS = FILTERS = BREAKDOWNS (POC 3 Pattern)

**Key Insight:** Users expect the same list of dimensions to appear in BOTH places:
1. **Sidebar filters** (left side of the page)
2. **Breakdown dropdown** (inside the drill-down modal)

**❌ WRONG (Separated Lists):**
```python
# Brief specifies:
# - Global Filters: Region, Department
# - Drill-Down Dimensions: Agent Group, Experience Type, Channel
```

**✅ CORRECT (Unified List):**
```python
# Brief specifies:
# - Dimensions (used for both filters AND breakdowns):
#   1. Region
#   2. Department  
#   3. Agent Group
#   4. Experience Type
#   5. Channel
```

**Implementation:**
1. When analyst lists dimensions in the brief, add ALL of them to:
   - `core/filter_config.py` (sidebar filters)
   - `services/snowflake_svc/drill_down/sql.py` FILTER_MAP (breakdown dimensions)
2. **Exception:** Skip dimensions with 20+ distinct values as sidebar filters (too many options), but keep as breakdown dimensions

**Example from POC 3:**
```python
# core/filter_config.py - 6 sidebar filters
FILTER_CONFIGS = {
    "working_region": FilterConfig(...),
    "handoff_bucket": FilterConfig(...),
    "business_impact": FilterConfig(...),
    "department": FilterConfig(...),
    "experience_type": FilterConfig(...),
    "channel": FilterConfig(...),
    # Agent Group skipped (50+ values)
}

# services/snowflake_svc/drill_down/sql.py - 7 breakdown dimensions
FILTER_MAP = {
    "Working Region": "REGION_BUCKET",
    "Handoffs": "HANDOFF_BUCKET",
    "Business Impact": "BUSINESS_IMPACT",
    "Department": "DEPARTMENT",
    "Experience Type": "ADV_EXP_TYPE",
    "Channel": "TICKET_CHANNEL",
    "Agent Group": "AGENT_GROUP_NAME",  # Include in breakdowns
}
```

**Why This Matters:**
- Reduces confusion about "is this a filter or a dimension?"
- Users expect symmetry: if I can filter by Region, I should be able to break down by Region
- Prevents the "I wanted 7 in both places" clarification question

---

...
**Why This Matters:**
- Reduces confusion about "is this a filter or a dimension?"
- Users expect symmetry: if I can filter by Region, I should be able to break down by Region
- Prevents the "I wanted 7 in both places" clarification question

### Rule 8: AUTONOMOUS DATA PROFILING & SAFE SQL CASTING (NEW)
When the Dashboard Brief requests a filter, dimension, or bucket (e.g., grouping "3, 4, 5" into a "3+" bin), **YOU are responsible for the final SQL syntax and type safety.** Before writing the service layer Python files, you must:
1. **Profile the Column:** Use the Snow CLI to check the data type of the requested column (e.g., `snow sql -q "SELECT TYPEOF(column) FROM table LIMIT 1"`).
2. **Apply Safe Casting:** If you are creating a `CASE` statement that mixes numbers and string labels (like `'3+'`), YOU must automatically write the SQL to wrap it in a string cast: `CAST(CASE... AS VARCHAR)`. Do not expect the user to provide this cast in their brief.
3. **Verify Execution:** Run a quick `COUNT(*)` group-by query using your generated `CASE` statement via Snow CLI. If Snowflake throws a `Numeric value is not recognized` error, fix your `CAST` logic before adding it to the Python code.

---

## COMMON SQL PATTERNS
...

## COMMON SQL PATTERNS

### Pattern 1: COALESCE for NULL Handling

When a dimension column has many NULLs (>20%), use COALESCE to create an "Unknown" bucket:

```sql
-- POC 3 Example: 49.7% of AGYLE_WORKING_REGION were NULL
BASE_CTE = """
WITH data AS (
    SELECT 
        TICKET_ID,
        COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET
    FROM Z2_TICKETS
    WHERE business_filter = TRUE
)
"""
```

**Filter Config:**
```python
FilterConfig(
    filter_id="working_region",
    sql_column="REGION_BUCKET",  # Reference computed column
    options=["AMER", "EMEA", "APAC", "LATAM", "Unknown"],  # Include "Unknown"
    default_label="All Regions"
)
```

### Pattern 2: CASE Statements for Bucketing

When a dimension has many distinct values that need grouping (e.g., 0-10 becomes "3+"):

```sql
-- POC 3 Example: TICKET_ASSIGNEE_STATIONS had values 0,1,2,3,4,5...
BASE_CTE = """
WITH data AS (
    SELECT 
        TICKET_ID,
        CASE
            WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
            WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
            WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
            WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
            ELSE 'Unknown'
        END AS HANDOFF_BUCKET
    FROM Z2_TICKETS
    WHERE business_filter = TRUE
)
"""
```

**CRITICAL:** Always include `ELSE 'Unknown'` clause to handle unexpected values.


**Filter Config:**
```python
FilterConfig(
    filter_id="handoff_bucket",
    sql_column="HANDOFF_BUCKET",  # Reference computed column
    options=["0", "1", "2", "3+"],  # Match CASE statement buckets
    default_label="All"
)
```

### Pattern 3: Time Window Aggregation

**7-day rolling window (daily trend):**
```sql
WHERE CREATED_TIMESTAMP >= DATEADD('day', -7, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()

-- Trend config
default_granularity="Daily"
```

**90-day rolling window (monthly trend):**
```sql
WHERE CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()

-- Trend config
default_granularity="Monthly"  -- Not daily (too many data points)
```

**Month-to-date (MTD):**
```sql
WHERE CREATED_TIMESTAMP >= DATE_TRUNC('month', CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
```

**Quarter-to-date (QTD):**
```sql
WHERE CREATED_TIMESTAMP >= DATE_TRUNC('quarter', CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
```

### Pattern 4: Discovering Filter Options

Before adding a dimension as a filter, run this query to see distinct values:

```bash
snow sql -q "
SELECT {DIMENSION_COLUMN}, COUNT(*) as count
FROM {TABLE}
WHERE {BUSINESS_FILTER}
GROUP BY {DIMENSION_COLUMN}
ORDER BY count DESC
LIMIT 50
"
```

**Decision rules:**
- **≤ 10 values:** Include as sidebar filter ✅
- **10-20 values:** Ask user if they want this as a filter
- **20+ values:** Skip as sidebar filter (too many options), keep as breakdown dimension only

**POC 3 Example:**
- Agent Group had 50+ distinct values → Excluded from sidebar filters
- Department had 13 values → Included as sidebar filter
- Working Region had 5 values (after COALESCE) → Included as sidebar filter

---

## EXECUTION WORKFLOW

When asked to build a dashboard based on a brief, follow these steps exactly:

### Step 1: Read and Validate the Brief
1. Read the provided `DASHBOARD_BRIEF.md`
2. Check for required information:
   - [ ] Data source (table name, schema)
   - [ ] Main KPI SQL query
   - [ ] Global filters definition
   - [ ] Drill-down dimensions
   - [ ] Business filter logic
3. **If ANY required information is missing, STOP and ask the user for clarification**

### Step 2: Create the Service Layer

**Step 2a: Identify Computed Filter Columns**

Before creating service files, check if ANY dimensions in the brief use:
1. **COALESCE** (e.g., `COALESCE(region, 'Unknown')`)
2. **CASE statements** (e.g., bucketing logic for "3+" handoffs)

If YES to either:
1. Define `BASE_CTE` in `services/snowflake_svc/{service}/sql.py`
2. Compute ALL filter columns in `BASE_CTE` with clear aliases (e.g., `REGION_BUCKET`, `HANDOFF_BUCKET`)
3. Use `BASE_CTE` for main KPI query
4. **Copy EXACT same BASE_CTE** to `services/snowflake_svc/drill_down/sql.py`
5. In `core/filter_config.py`, reference the computed aliases, NOT the CASE statement or raw column

**Example:**
```python
# services/snowflake_svc/z2_tickets/sql.py
BASE_CTE = """
WITH z2_capacity_data AS (
    SELECT 
        TICKET_ID,
        COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET,
        CASE
            WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
            ELSE CAST(TICKET_ASSIGNEE_STATIONS AS VARCHAR)
        END AS HANDOFF_BUCKET
    FROM Z2_TICKETS
    WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
)
"""

MAIN_KPI = BASE_CTE + "SELECT COUNT(TICKET_ID) FROM z2_capacity_data"

# core/filter_config.py
FilterConfig(
    sql_column="REGION_BUCKET",  # ✅ Reference computed column
    ...
)

FilterConfig(
    sql_column="HANDOFF_BUCKET",  # ✅ Reference computed column
    ...
)
```

**Why This Matters:** Prevents "invalid identifier" errors when filters are applied (Rule 6).

**Step 2b: Create Service Files**

Create `services/snowflake_svc/{service_name}/`:
- `__init__.py` - Export service functions
- `sql.py` - SQL queries (use EXACT SQL from the brief, include BASE_CTE if needed)
- `service.py` - Service functions with `@st.cache_data`

**Critical:** Use the user's SQL queries EXACTLY as provided. Do not modify them.

Connect global filters to the `where_sql` parameter:
```python
@st.cache_data(ttl=3600)
def fetch_my_kpi(where_sql: str) -> pd.DataFrame:
    session = get_snowflake_session()
    if session is None:
        return pd.DataFrame({'ACTUAL': [mock_value], 'TARGET': [mock_value]})
    
    query = sql.MY_KPI_QUERY
    if where_sql and where_sql != "1=1":
        query = query.replace(
            "WHERE CREATED_TIMESTAMP",
            f"WHERE {where_sql} AND CREATED_TIMESTAMP"
        )
    return session.sql(query).to_pandas()
```

### Step 3: Update Filter Configuration

If the brief specifies global filters, add them to `core/filter_config.py`:

**CRITICAL:** When defining `FilterConfig`, check the BASE_CTE. If the filter column is computed using `AS alias_name`, you MUST set `sql_column="alias_name"`. NEVER use the raw column or the CASE logic in the `sql_column` field.

```python
FILTER_CONFIGS = {
    # Existing demo filters...
    
    # New filters from brief
    "my_filter": FilterConfig(
        filter_id="my_filter",
        label="My Filter Label",
        session_key="filter_my_filter",
        sql_column="SQL_COLUMN_NAME",  # If BASE_CTE uses "AS COLUMN_NAME", reference the alias
        options=["Option1", "Option2"],  # From brief
        default_label="All"
    ),
}
```

**Example - Computed Filter Column:**
```python
# If BASE_CTE has: CASE WHEN stations >= 3 THEN '3+' END AS HANDOFF_BUCKET

# ✅ CORRECT:
FilterConfig(
    sql_column="HANDOFF_BUCKET",  # Reference the alias from BASE_CTE
    ...
)

# ❌ WRONG:
FilterConfig(
    sql_column="TICKET_ASSIGNEE_STATIONS",  # Raw column doesn't exist in CTE!
    ...
)

# ❌ WRONG:
FilterConfig(
    sql_column="CASE WHEN stations >= 3 THEN '3+' END",  # Never put CASE in filter_config!
    ...
)
```

### Step 4: Update Drill-Down Dimensions
If the brief specifies drill-down dimensions, add them to `services/snowflake_svc/drill_down/sql.py`:

```python
FILTER_MAP = {
    # Existing demo dimensions...
    
    # New dimensions from brief
    "My Dimension": "SQL_COLUMN_NAME",  # From brief
}
```

Update `BASE_CTE` in the same file to match the user's table and columns.

### Step 5: Register Metrics
Create `metrics/definitions/{domain}.py`:

**CRITICAL:** Check the brief to see if the metric **has a target**. This changes the configuration!

#### Scenario A: Metric WITH Target
```python
from metrics.metric import Metric
from metrics.registry import register
from ui.components.donut_card_config import DonutCardConfig
from ui.components.formatters import FormatType
from services import snowflake_svc

def register_all():
    register(Metric(
        key="my_metric_key",
        title="My Metric Title",
        help_text="Description from brief",
        donut_config=DonutCardConfig(
            service_fn=snowflake_svc.fetch_my_kpi,
            actual_col="ACTUAL_COLUMN",
            target_qtd_col="TARGET_COLUMN",  # ← Include target
            format_type=FormatType.NUMBER,
            thresholds={'green': 1.0, 'yellow': 0.95},  # ← Include thresholds
            yoy_actual_col="ACTUAL_COLUMN",  # Optional
            yoy_ly_col="LY_COLUMN",          # Optional
        ),
        show_yoy=True,  # If YoY in brief
        show_pacing_target=True,
    ))
```

#### Scenario B: Metric WITHOUT Target
```python
def register_all():
    register(Metric(
        key="my_metric_key",
        title="My Metric Title",
        help_text="Description from brief",
        donut_config=DonutCardConfig(
            service_fn=snowflake_svc.fetch_my_kpi,
            actual_col="ACTUAL_COLUMN",
            target_qtd_col=None,  # ← No target
            format_type=FormatType.NUMBER,
            thresholds=None,  # ← No thresholds
            yoy_actual_col="ACTUAL_COLUMN",  # Optional
            yoy_ly_col="LY_COLUMN",          # Optional
        ),
        show_yoy=True,  # If YoY in brief
        show_pacing_target=False,  # ← No target pacing
    ))
```

**If the brief includes drill-downs**, add DrillConfig:

```python
from ui.components.drill_config import DrillConfig
from ui.components.drill_tabs.breakdown_config import BreakdownTabConfig
from services.snowflake_svc.drill_down.sql import FILTER_MAP

_BREAKDOWN = BreakdownTabConfig(
    filter_map=FILTER_MAP,
    format_type=FormatType.NUMBER,
)

# Add to the Metric() call above:
drill_config=DrillConfig(
    drill_key="drill_my_metric",
    drill_title="My Metric Breakdown",
    tabs=["breakdown"],  # ← Or ["breakdown", "trend"] if trend requested
    modal_filters=[],
    breakdown_config=_BREAKDOWN,
)
```

**If the brief requests a Trend tab** (Section 4.1), add TrendTabConfig:

```python
from ui.components.drill_tabs.trend_config import TrendTabConfig

_TREND = TrendTabConfig(
    date_column="CREATED_TIMESTAMP",  # From brief
    default_granularity="Daily",       # From brief
    format_type=FormatType.NUMBER      # Matches donut_config format_type
)

# Update DrillConfig to include trend tab:
drill_config=DrillConfig(
    drill_key="drill_my_metric",
    drill_title="My Metric Breakdown",
    tabs=["breakdown", "trend"],  # ← Add "trend"
    modal_filters=[],
    breakdown_config=_BREAKDOWN,
    trend_config=_TREND,           # ← Add trend config
)
```

**CRITICAL:** The `format_type` in `TrendTabConfig` MUST match the `format_type` in `DonutCardConfig`. This ensures the Y-axis and tooltips are formatted consistently (e.g., currency vs count vs percentage).

### Built-In Feature: Click-to-Export CSV

**The template automatically includes CSV export functionality!** Users can click any bar in the breakdown chart to export those specific records.

**What it does:**
- Adds "💾 Export by Slice" section below breakdown chart (collapsible like "View Data Table")
- Users expand any dimension value (e.g., "AMER: 6,200 tickets")
- Shows SQL filter that will be applied
- Click "📥 Export" → Downloads CSV with all columns matching that slice
- Uses the same BASE_CTE as charts (guaranteed filter consistency)
- Includes 100,000 row safety limit

**You don't need to configure anything!** It works automatically for all dashboards.

**How it works behind the scenes:**
1. User clicks breakdown: "Working Region: AMER (6,200 tickets)"
2. System builds WHERE clause: `HANDOFF_BUCKET = '0' AND REGION_BUCKET = 'AMER'`
3. Executes: `SELECT * FROM base_cte WHERE {combined_filters} LIMIT 100000`
4. Returns CSV with all ticket-level columns

**User sees:**
```
▶ 📊 View Data Table
▶ 💾 Export by Slice    ← Automatically available!
  ├─ 📊 AMER (6,200 records)
  │   Filters: HANDOFF_BUCKET = '0' AND REGION_BUCKET = 'AMER'
  │   [📥 Export 6,200 records]
  ├─ 📊 EMEA (200 records)
  └─ ...
```

**CRITICAL:** Update two files to make the metric discoverable:

1. **`metrics/definitions/__init__.py`** - Export the new module:
```python
from . import demo, z2_tickets  # Add your module here

__all__ = ['demo', 'z2_tickets']  # Add to exports
```

2. **`metrics/loader.py`** - Call the new `register_all()` function:
```python
def register_all():
    definitions.demo.register_all()
    definitions.z2_tickets.register_all()  # Add this line
```

### Step 6: Create UI Page
Create `ui/pages/{page_name}.py`:

```python
import streamlit as st
import metrics as metric_registry
from ui.components.donut_card import render_donut_card
from ui.components.filters import render_filters

def render():
    """Main render function for this page."""
    metric_registry.register_all()
    
    try:
        # Render global filters
        where_sql = render_filters(
            namespace="{page_name}",
            available_filters=["filter1", "filter2"],  # From brief
            default_where="1=1"
        )
        
        # Page header
        st.header("📊 {Page Title}")
        st.markdown("{Description from brief}")
        
        # Render metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            render_donut_card("my_metric_key", where_sql)
        
    except Exception as e:
        st.error("Error loading {page_name} page.")
        st.exception(e)
```

Update `streamlit_app.py` to add the new page to navigation.

### Step 7: Self-Check Before Finalizing

**STOP and verify you completed these critical steps:**

- [ ] Created service layer in `services/snowflake_svc/{service_name}/`
- [ ] **CRITICAL (Rule 6):** If filters use CASE/COALESCE, BASE_CTE is defined in service sql.py
- [ ] **CRITICAL (Rule 6):** Same BASE_CTE copied to `drill_down/sql.py`
- [ ] **CRITICAL (Rule 6):** `filter_config.py` references computed column aliases (e.g., "BUCKET") not CASE statements
- [ ] Added filters to `core/filter_config.py` (if brief specified global filters)
- [ ] Updated `services/snowflake_svc/drill_down/sql.py` FILTER_MAP (if brief specified drill dimensions)
- [ ] Created metric definition in `metrics/definitions/{domain}.py`
- [ ] **CRITICAL:** Updated `metrics/definitions/__init__.py` to export new module
- [ ] **CRITICAL:** Updated `metrics/loader.py` to call new `register_all()`
- [ ] **CRITICAL:** Verified `fetch_trend_data` is exported in `services/snowflake_svc/__init__.py` (if trend tab requested)
- [ ] **CRITICAL:** Verified formatter aliases exist in `ui/components/formatters.py` (format_currency, format_number, format_percentage)
- [ ] Created UI page in `ui/pages/{page_name}.py`
- [ ] **CRITICAL:** Updated `ui/pages/__init__.py` to export new page (if demo was deleted)
- [ ] Updated `streamlit_app.py` navigation
- [ ] **CRITICAL:** Removed any `st.info()` messages in `services/snowflake_svc/session.py`

**If ANY of these are incomplete, go back and finish them before Step 7a.**

### Step 7a: Import Validation

After creating new modules, IMMEDIATELY test imports:
```bash
python3 -c "import services; import metrics; import ui.pages; print('✅ All imports successful')"
```

If ImportError occurs:
1. Check `services/snowflake_svc/__init__.py` exports new service
2. Check `metrics/definitions/__init__.py` exports new metric module
3. Check `ui/pages/__init__.py` exports new page
4. Verify no deleted modules (like demo) are still imported

**If imports fail, fix them before proceeding to Step 8.**

### Step 8: Generate README with Validation Checklist
**CRITICAL FINAL STEP:** Overwrite the repository's `README.md` with:

1. Quick start instructions
2. Data source information from the brief
3. The following validation checklist:

```markdown
## Validation Checklist

Run these checks to verify the dashboard works:

- [ ] **Import test passes:**
  ```bash
  python -c "from services.snowflake_svc import {service_name}"
  ```

- [ ] **SQL queries execute (test with Snow CLI):**
  ```bash
  snow sql -q "SELECT COUNT(*) FROM {table_name} WHERE {business_filter}"
  ```

- [ ] **App launches:**
  ```bash
  streamlit run streamlit_app.py
  ```

- [ ] **Main scorecard shows correct data**
  - Expected value: {expected_value_from_sql}
  - Actual value: _____ (fill in after running)

- [ ] **Drill-down modal opens**
  - Click "Details" button → modal appears

- [ ] **Breakdown charts render**
  - Test each dimension from the brief

- [ ] **Global filters work**
  - Change filter values → KPI updates
```

---

## PRE-GENERATION CHECKLIST (CRITICAL - STOP AND READ)

**CRITICAL PRE-FLIGHT CHECK:** Before writing any Python files, you MUST review the Brief. If **ANY** of the following are missing, output the exact phrase: 

```
🚨 BRIEF INCOMPLETE: Please clarify [Missing Item] before I generate the code.
```

**And STOP. Do not generate code.**

**Required Items:**
- [ ] **Has Target?** explicitly answered (YES/NO)
- [ ] **Has YoY?** explicitly answered (YES/NO)
- [ ] **Has Trend Tab?** explicitly answered (YES/NO)
- [ ] **Time Window** specified (7-day, 30-day, 90-day, MTD, QTD, etc.)
- [ ] **Main KPI SQL query** runs successfully in Snow CLI
- [ ] **Expected value** is documented (e.g., "~112,411 tickets")
- [ ] **Dimensions** list includes SQL column names (not just labels)
- [ ] **NULL Handling Strategy** documented if dimensions can be NULL

**SQL Validation Checks:**
- [ ] CASE statements include `ELSE 'Unknown'` clause
- [ ] Filter values were extracted with `SELECT DISTINCT` (not guessed)

**Configuration Clarity:**
- [ ] If "Has Trend Tab? YES", date column and granularity are specified
- [ ] If "Has Target? YES", target column name is specified
- [ ] If dimensions use COALESCE or CASE, computed aliases are documented

**If ANY checkbox is unchecked, STOP and ask analyst before generating code.**

---

## COMMON PITFALLS TO AVOID

### ❌ Pitfall 1: Guessing Column Names
**WRONG:**
```python
actual_col="REVENUE"  # Guessed!
```

**RIGHT:**
```python
# Stop and ask: "What is the exact column name for the actual value?"
```

### ❌ Pitfall 2: Hardcoding Business Logic in UI
**WRONG:**
```python
# In ui/pages/my_page.py
df = session.sql("SELECT COUNT(*) FROM Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE")
```

**RIGHT:**
```python
# In services/snowflake_svc/my_service/sql.py
BASE_CTE = """
WITH filtered_data AS (
    SELECT * FROM Z2_TICKETS
    WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
)
"""
```

### ❌ Pitfall 3: Creating New Component Types
**WRONG:**
```python
# Creating a new "bar_chart_card.py" component
```

**RIGHT:**
```python
# Use existing donut_card.py with different format_type
```

### ❌ Pitfall 4: Assuming All Metrics Have Targets
**WRONG:**
```python
# Always including target_qtd_col even when brief says "Has Target? NO"
donut_config=DonutCardConfig(
    actual_col="VALUE",
    target_qtd_col="TARGET",  # Brief said no target!
)
```

**RIGHT:**
```python
# Check the brief's "Has Target?" field
# If NO:
donut_config=DonutCardConfig(
    actual_col="VALUE",
    target_qtd_col=None,  # No target
    thresholds=None,      # No attainment thresholds
)
```

**Visual difference:**
- **WITH target:** Gauge chart + delta + attainment colors
- **WITHOUT target:** Just the value (cleaner, simpler display)

---

## COMMON PITFALLS (LESSONS LEARNED FROM POC 3-4)

These are real errors that occurred during dashboard development. Learn from them to avoid repeating mistakes.

### ❌ Pitfall 5: Referencing Raw Columns Instead of BASE_CTE Aliases
**Error:** `SnowparkSQLException: invalid identifier 'REGION_BUCKET'`

**What happened:**
- Brief requested filter: "Working Region" with COALESCE for NULL handling
- BASE_CTE computed: `COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET`
- But filter_config.py referenced the raw column: `sql_column="AGYLE_WORKING_REGION"`
- When filter was applied, SQL tried to use AGYLE_WORKING_REGION which doesn't exist in the CTE output

**WRONG:**
```python
# services/snowflake_svc/my_service/sql.py
BASE_CTE = """
WITH data AS (
    SELECT COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET
    FROM Z2_TICKETS
)
"""

# core/filter_config.py
FilterConfig(
    sql_column="AGYLE_WORKING_REGION",  # ❌ Raw column doesn't exist in CTE!
    options=["AMER", "EMEA", "APAC"]
)
```

**RIGHT:**
```python
# core/filter_config.py
FilterConfig(
    sql_column="REGION_BUCKET",  # ✅ Reference the computed alias
    options=["AMER", "EMEA", "APAC", "Unknown"]  # Include "Unknown" in options
)
```

**Rule:** Always reference computed column aliases from BASE_CTE, never raw table columns when using COALESCE/CASE.

---

### ❌ Pitfall 6: CASE Statement Type Mixing Without CAST
**Error:** `SnowparkSQLException: Numeric value '3+' is not recognized`

**What happened:**
- Brief requested bucketing: Group ticket handoffs "0,1,2" individually and "3,4,5..." as "3+"
- Generated CASE statement mixed integers (0,1,2) with string ('3+')
- Snowflake couldn't determine if the result should be NUMBER or VARCHAR

**WRONG:**
```python
CASE
    WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN 0
    WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN 1
    WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN 2
    WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'  # ❌ String mixed with numbers!
END AS HANDOFF_BUCKET
```

**RIGHT:**
```python
CASE
    WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'  # ✅ All strings
    WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
    WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
    WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
    ELSE 'Unknown'  # ✅ Always include ELSE
END AS HANDOFF_BUCKET
```

**Rule:** When CASE statement includes string labels like '3+', convert ALL return values to strings. Always include ELSE clause.

---

### ❌ Pitfall 7: Assuming All Metrics Have TARGET Column
**Error:** `KeyError: 'TARGET'` in breakdown_tab.py line 122

**What happened:**
- POC 4 metric was configured with `target_qtd_col=None` (brief said "Has Target? NO")
- breakdown_tab.py assumed TARGET column always exists: `row["TARGET"]`
- Code crashed when trying to access non-existent column

**WRONG:**
```python
# ui/components/drill_tabs/breakdown_tab.py
def _render_chart(df, dimension_name, format_type):
    df["ATTAINMENT"] = df.apply(
        lambda row: row["ACTUAL"] / row["TARGET"],  # ❌ Assumes TARGET exists!
        axis=1
    )
```

**RIGHT:**
```python
def _render_chart(df, dimension_name, format_type):
    # Check if metric has a target before using TARGET column
    has_target = "TARGET" in df.columns and pd.notnull(df["TARGET"]).any()
    
    if has_target:
        # Show attainment colors
        df["ATTAINMENT"] = df.apply(lambda row: row["ACTUAL"] / row["TARGET"], axis=1)
        chart = alt.Chart(df).mark_bar().encode(color="COLOR", ...)
    else:
        # Simple green bars for metrics without targets
        chart = alt.Chart(df).mark_bar(color=CACTUS).encode(...)
```

**Rule:** Always check column existence before accessing it. Not all metrics have targets, YoY, or trend tabs.

---

### ❌ Pitfall 8: Indentation in Nested Code Blocks
**Error:** `IndentationError: expected an indented block after 'with' statement on line 217`

**What happened:**
- Added code inside nested blocks: `with expander → for loop → if statement`
- Forgot to increase indentation at each nesting level
- Python couldn't parse the structure

**WRONG:**
```python
with st.expander("💾 Export by Slice"):
    st.caption("Instructions")
    for idx, row in df.iterrows():
    dim_value = row['DIM_VALUE']  # ❌ Should be indented 8 spaces (2 levels)
```

**RIGHT:**
```python
with st.expander("💾 Export by Slice"):
    st.caption("Instructions")  # 4 spaces (1 level)
    for idx, row in df.iterrows():  # 4 spaces (1 level)
        dim_value = row['DIM_VALUE']  # 8 spaces (2 levels)
        with st.expander(f"{dim_value}"):  # 8 spaces
            if st.button("Export"):  # 12 spaces (3 levels)
                do_export()  # 16 spaces (4 levels)
```

**Rule:** Each nesting level (with/for/if/def) adds 4 spaces. Count your nesting depth carefully.

---

### ❌ Pitfall 9: Top N + Other Bucketing Without Strategy
**What happened:**
- Brief requested "Channel" dimension
- Discovery query showed 12 distinct values
- Some values had 20K+ tickets, others had <100 tickets
- Including all 12 as filter options would clutter the sidebar

**WRONG (Naive Approach):**
```python
# Just dump all 12 values in the filter
FilterConfig(
    filter_id="channel",
    options=["Native Messaging", "Mail", "Web form", "Chat", "Web service", 
             "API", "Closed Ticket", "Mobile", "Voice", "SMS", "Help center", "Other"]  # ❌ Too many!
)
```

**RIGHT (Top N + Other Pattern):**
```python
# Step 1: Run discovery query to see distribution
snow sql -q "
SELECT TICKET_CHANNEL, COUNT(*) as count
FROM Z2_TICKETS
WHERE business_filter = TRUE
GROUP BY TICKET_CHANNEL
ORDER BY count DESC
"

# Results showed:
# Native Messaging: 35,000 (31%)
# Mail: 28,000 (25%)
# Web form: 20,000 (18%)
# Web service: 15,000 (13%)
# Closed Ticket: 8,000 (7%)
# [7 other values]: 6,000 combined (5%)

# Step 2: Create computed column for Top 5 + Other
BASE_CTE = """
WITH data AS (
    SELECT 
        CASE
            WHEN TICKET_CHANNEL IN ('Native Messaging', 'Mail', 'Web form', 'Web service', 'Closed Ticket') 
                THEN TICKET_CHANNEL
            ELSE 'Other'
        END AS CHANNEL_BUCKET
    FROM Z2_TICKETS
)
"""

# Step 3: Filter config references the bucket
FilterConfig(
    filter_id="channel",
    sql_column="CHANNEL_BUCKET",
    options=["Native Messaging", "Mail", "Web form", "Web service", "Closed Ticket", "Other"]  # ✅ Only 6 options
)
```

**Rule:** For dimensions with 10+ values, check the distribution. Group low-volume values as "Other" to keep UI clean.

---

### ❌ Pitfall 10: Forgetting to Update __init__.py After Adding Modules
**Error:** `ModuleNotFoundError: No module named 'metrics.definitions.z2_tickets'`

**What happened:**
- Created new metric definition file: `metrics/definitions/z2_tickets.py`
- Called `register_all()` in `metrics/loader.py`
- Forgot to export the module in `metrics/definitions/__init__.py`
- Import failed when app tried to load metrics

**WRONG:**
```python
# metrics/definitions/__init__.py (forgot to update)
from . import demo

__all__ = ['demo']  # ❌ Missing z2_tickets export
```

**RIGHT:**
```python
# metrics/definitions/__init__.py
from . import demo, z2_tickets  # ✅ Add new module

__all__ = ['demo', 'z2_tickets']  # ✅ Add to exports
```

**Files to update after adding new modules:**
1. `services/snowflake_svc/__init__.py` - Export new service functions
2. `metrics/definitions/__init__.py` - Export new metric definition module
3. `ui/pages/__init__.py` - Export new page module
4. **Verify immediately:** `python3 -c "import services; import metrics; import ui.pages"`

**Rule:** After creating ANY new Python module, update its parent `__init__.py` to export it. Test imports immediately.

---

## SUCCESS CRITERIA

The dashboard is complete when:

1. ✅ All SQL queries come directly from the brief (no guessing)
2. ✅ Service layer properly caches data with `@st.cache_data`
3. ✅ Metrics are registered in the registry (not hardcoded in pages)
4. ✅ Global filters work and pass through to drill-downs
5. ✅ README contains a complete validation checklist
6. ✅ No SQL queries exist in the `ui/` folder
7. ✅ Mock data is provided for local testing (when `USE_MOCK_DATA=True`)
8. ✅ All imports pass: `python -c "from services.snowflake_svc import {service}"`

---

## WHEN IN DOUBT

**Ask the user for clarification.** It is better to ask 5 questions than to generate a dashboard that doesn't match their data.

Remember: **You are a code generator, not a data analyst.** The user knows their data. You know the architecture.
