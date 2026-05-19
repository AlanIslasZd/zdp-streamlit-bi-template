# Dashboard Brief: Z2 Tickets - Advocacy Capacity Planning

**Dashboard Name:** `zdp-streamlit-metrics-z2_tickets_poc_3`  
**Created By:** Alan (POC 3 - Reflects actual implementation)  
**Date:** 2026-05-18

---

## 0. Quick Decision Summary

**Answer these questions first to guide your implementation:**

| Question | Answer | Notes |
|----------|--------|-------|
| **Has Target?** | NO | Count-only metric, no target column |
| **Has YoY?** | NO | Last year data not available yet |
| **Has Trend Tab?** | YES | Monthly aggregation (90-day window) |
| **Time Window** | 90 days | Quarterly capacity planning view |
| **NULL Strategy** | Explicit "Unknown" option | 49.7% of regions are NULL |
| **Bucketing Logic** | CASE for "3+" handoffs | Validated with Snow CLI |
| **Number of Dimensions** | 7 total | 6 in sidebar filters, 7 in breakdowns |

---

## 1. Data Source

**Table:** `FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS`

**Business Filter (Applied to ALL queries):**
```sql
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
```

**Rationale:** 
- `ADV_TICKET_FILTER_CAPACITY = TRUE` excludes automated resolutions and tickets that never reached a human agent
- Last 90 days provides quarterly capacity planning view (sufficient for monthly trend analysis)

**Validation Query:**
```bash
snow sql -q "
SELECT COUNT(TICKET_ID) AS TICKET_COUNT
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
"
```

**Expected Result:** ~112,411 tickets (validated 2026-05-18)

---

## 2. Dimensions (Used for BOTH Filters and Breakdowns)

**IMPORTANT:** These dimensions appear in BOTH places:
1. **Sidebar filters** (left side of page) - 6 dimensions (Agent Group skipped due to 50+ values)
2. **Breakdown dropdown** (inside drill-down modal) - All 7 dimensions

**Total Dimensions:** 7 (Agent Group excluded from sidebar filters due to 50+ distinct values)

### Dimension 1: Working Region

- **SQL Column (Raw):** `AGYLE_WORKING_REGION`
- **SQL Column (Computed):** `COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET`
- **Data Type:** VARCHAR
- **Values:** `["AMER", "EMEA", "APAC", "LATAM", "Unknown"]`
- **NULL Handling:** Show as "Unknown" (49.7% of tickets have NULL region)
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT 
    COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET,
    COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY REGION_BUCKET
ORDER BY count DESC
"
```

**Expected Values:**
- Unknown: 55,795 (49.7%)
- EMEA: 21,623
- AMER: 20,016
- APAC: 11,404
- LATAM: 3,573

**Why COALESCE?** Almost half the records are NULL. Showing "Unknown" is better UX than filtering them out.

---

### Dimension 2: Handoffs (Assignee Stations)

- **SQL Column (Raw):** `TICKET_ASSIGNEE_STATIONS` (INTEGER)
- **SQL Column (Computed):** Computed as `HANDOFF_BUCKET` in BASE_CTE
- **Data Type:** VARCHAR (computed from INTEGER)
- **Values:** `["0", "1", "2", "3+"]`
- **NULL Handling:** N/A (no NULLs observed)
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**CASE Statement Logic:**
```sql
CASE
    WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
    WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
    WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
    WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
    ELSE 'Unknown'
END AS HANDOFF_BUCKET
```

**Validation Query:**
```bash
snow sql -q "
SELECT 
    CASE
        WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
        WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
        WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
        WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
        ELSE 'Unknown'
    END AS HANDOFF_BUCKET,
    COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY HANDOFF_BUCKET
ORDER BY count DESC
"
```

**Expected Values:**
- 1: 80,634 (71.8%)
- 2: 17,306
- 3+: 7,931
- 0: 6,540

**Why CASE Statement?** Bucketing "3, 4, 5, 6..." into "3+" reduces clutter in the UI.

---

### Dimension 3: Business Impact (Severity)

- **SQL Column:** `BUSINESS_IMPACT`
- **Data Type:** VARCHAR
- **Values:** `["1 Critical", "2 Major", "3 Moderate", "4 Limited"]`  
  **IMPORTANT:** Values use SPACE (e.g., "1 Critical"), NOT dash (not "1 - Critical")
- **NULL Handling:** 1,399 NULLs exist (1.2% of records) - keep in data
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT BUSINESS_IMPACT, COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY BUSINESS_IMPACT
ORDER BY count DESC
"
```

**Expected Values:**
- 3 Moderate: 79,852
- 4 Limited: 15,140
- 2 Major: 11,341
- 1 Critical: 4,679
- NULL: 1,399

**⚠️ Common Mistake:** Do NOT use "1 - Critical" (with dash). The actual values have spaces.

---

### Dimension 4: Department

- **SQL Column:** `DEPARTMENT`
- **Data Type:** VARCHAR
- **Values:** 13 distinct departments (see validation query)
- **NULL Handling:** Minimal NULLs observed
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT DEPARTMENT, COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY DEPARTMENT
ORDER BY count DESC
"
```

**Top Values:**
- Advocacy
- RevOps
- Online Sales
- ProServe
- Sales
- Success
- (plus 7 more)

**Filter Options:** List all 13 departments in `filter_config.py` options array.

---

### Dimension 5: Experience Type

- **SQL Column:** `ADV_EXP_TYPE`
- **Data Type:** VARCHAR
- **Values:** `["Core", "Core+ Enhanced", "Core+ Essentials", "Enterprise", "Non-English Language"]`
- **NULL Handling:** Minimal NULLs observed
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT ADV_EXP_TYPE, COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY ADV_EXP_TYPE
ORDER BY count DESC
"
```

**Expected Values:** 5 experience types as listed above.

---

### Dimension 6: Channel

- **SQL Column:** `TICKET_CHANNEL`
- **Data Type:** VARCHAR
- **Values:** `["Native Messaging", "Mail", "Web form", "Web service", "Phone"]`
- **NULL Handling:** Minimal NULLs observed
- **Include in Sidebar Filter?** YES
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT TICKET_CHANNEL, COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY TICKET_CHANNEL
ORDER BY count DESC
"
```

**Expected Values:** 5 channels as listed above.

---

### Dimension 7: Agent Group Name

- **SQL Column:** `AGENT_GROUP_NAME`
- **Data Type:** VARCHAR
- **Distinct Values:** 50+ agent groups
- **NULL Handling:** Minimal NULLs observed
- **Include in Sidebar Filter?** NO (too many values for dropdown)
- **Include in Breakdown?** YES

**Validation Query:**
```bash
snow sql -q "
SELECT AGENT_GROUP_NAME, COUNT(*) AS count
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY AGENT_GROUP_NAME
ORDER BY count DESC
LIMIT 20
"
```

**Top Values:**
- Advocacy - Customer Care English
- RevOps - Customer Support
- Advocacy - Tier 2
- (plus 47 more)

**Why exclude from sidebar filter?** 50+ options in a multiselect crashes the UX. Keep as breakdown dimension only.

---

## 3. Main KPI (Scorecard)

### Scorecard 1: Advocacy Capacity Tickets

**Metric Name:** `advocacy_capacity_tickets`

**SQL Query (with BASE_CTE):**

**CRITICAL:** Use BASE_CTE to compute filter columns ONCE. This ensures sidebar filters and drill-downs reference the same computed columns.

```sql
WITH z2_capacity_data AS (
    SELECT
        TICKET_ID,
        AGENT_GROUP_NAME,
        DEPARTMENT,
        ADV_EXP_TYPE,
        TICKET_CHANNEL,
        CREATED_TIMESTAMP,
        COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET,
        CASE
            WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
            WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
            WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
            WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
            ELSE 'Unknown'
        END AS HANDOFF_BUCKET,
        BUSINESS_IMPACT
    FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
    WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
      AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
      AND CREATED_TIMESTAMP < CURRENT_DATE()
)
SELECT
    COUNT(TICKET_ID) AS TICKET_COUNT
FROM z2_capacity_data
```

**Expected Result:** ~112,411 tickets (validated 2026-05-18)

**Configuration:**
- **Format:** Number (ticket count)
- **Actual Column:** `TICKET_COUNT`
- **Target Column:** `None` (No target for this metric)
- **YoY Column:** `None` (Not implemented yet)
- **Thresholds:** `None` (No attainment colors without a target)
- **Has Target?** NO
- **Has YoY?** NO
- **Show Pacing Target?** NO

**Why no target?** This is a count-only metric. The visual will show just the number (cleaner, simpler display).

---

## 4. Drill-Down Configuration

### 4.1 Breakdown Tab

**Available Dimensions:** All 7 dimensions from Section 2

**Breakdown Query Template:**
```sql
-- Use SAME BASE_CTE as main KPI query
WITH z2_capacity_data AS (
    SELECT
        TICKET_ID,
        AGENT_GROUP_NAME,
        DEPARTMENT,
        ADV_EXP_TYPE,
        TICKET_CHANNEL,
        CREATED_TIMESTAMP,
        COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET,
        CASE
            WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
            WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
            WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
            WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
            ELSE 'Unknown'
        END AS HANDOFF_BUCKET,
        BUSINESS_IMPACT
    FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
    WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
      AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
      AND CREATED_TIMESTAMP < CURRENT_DATE()
)
SELECT
    {dimension_sql} AS DIM_VALUE,
    COUNT(TICKET_ID) AS ACTUAL,
    COUNT(TICKET_ID) AS TARGET
FROM z2_capacity_data
WHERE {where_sql}
GROUP BY DIM_VALUE
ORDER BY ACTUAL DESC
```

**Dimension Mapping (for drill_down/sql.py FILTER_MAP):**
```python
FILTER_MAP = {
    "Agent Group": "AGENT_GROUP_NAME",
    "Department": "DEPARTMENT",
    "Experience Type": "ADV_EXP_TYPE",
    "Channel": "TICKET_CHANNEL",
    "Working Region": "REGION_BUCKET",      # ← Computed alias
    "Handoffs": "HANDOFF_BUCKET",           # ← Computed alias
    "Business Impact": "BUSINESS_IMPACT",
}
```

**⚠️ CRITICAL:** Use the computed aliases (`REGION_BUCKET`, `HANDOFF_BUCKET`) in the FILTER_MAP, NOT the raw columns or CASE statements.

---

### 4.2 Trend Tab

**Does this metric need a Trend tab?** YES

**Configuration:**
- **Date Column for X-Axis:** `CREATED_TIMESTAMP`
- **Default Granularity:** `Monthly` (not Daily - 90 days would be 90 data points)
- **Expected Time Range:** Last 90 days (3 months)
- **Format Type:** `FormatType.NUMBER` (must match donut_config format_type)

**Trend Query Template:**
```sql
-- Use SAME BASE_CTE as main KPI query
WITH z2_capacity_data AS (
    SELECT
        TICKET_ID,
        AGENT_GROUP_NAME,
        DEPARTMENT,
        ADV_EXP_TYPE,
        TICKET_CHANNEL,
        CREATED_TIMESTAMP,
        COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET,
        CASE
            WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
            WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
            WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
            WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
            ELSE 'Unknown'
        END AS HANDOFF_BUCKET,
        BUSINESS_IMPACT
    FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
    WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
      AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
      AND CREATED_TIMESTAMP < CURRENT_DATE()
)
SELECT
    DATE_TRUNC('MONTH', CREATED_TIMESTAMP) AS PERIOD,
    TO_CHAR(DATE_TRUNC('MONTH', CREATED_TIMESTAMP), 'YYYY-MM') AS LBL,
    COUNT(TICKET_ID) AS VALUE
FROM z2_capacity_data
WHERE {where_sql}
GROUP BY PERIOD, LBL
ORDER BY PERIOD ASC
```

**Validation Query:**
```bash
snow sql -q "
SELECT 
    DATE_TRUNC('MONTH', CREATED_TIMESTAMP) AS PERIOD,
    TO_CHAR(DATE_TRUNC('MONTH', CREATED_TIMESTAMP), 'YYYY-MM') AS LBL,
    COUNT(TICKET_ID) AS VALUE
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
GROUP BY PERIOD, LBL
ORDER BY PERIOD ASC
"
```

**Expected:** 3 rows (one per month), values ranging ~30,000-45,000 tickets per month.

**Why Monthly?** 90 days with daily granularity would produce 90 data points (too noisy). Monthly aggregation produces 3 clean data points.

---

## 5. Page Layout

### Page 1: Advocacy Capacity

**File:** `ui/pages/advocacy_capacity.py`

**URL Path:** `/advocacy-capacity` (configured in `streamlit_app.py`)

**Sidebar Filters:** 6 filters (available_filters list in render_filters call):
```python
available_filters=[
    "working_region",
    "handoff_bucket",
    "business_impact",
    "department",
    "experience_type",
    "channel"
]
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  Sidebar: Global Filters                        │
│  □ Working Region (5 options)                   │
│  □ Handoffs (4 options)                         │
│  □ Business Impact (4 options)                  │
│  □ Department (13 options)                      │
│  □ Experience Type (5 options)                  │
│  □ Channel (5 options)                          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Header: 📞 Advocacy Capacity Planning          │
│  Data Source: Z2_TICKETS (Last 90 Days)         │
│  Filter Logic: ADV_TICKET_FILTER_CAPACITY=TRUE  │
└─────────────────────────────────────────────────┘

┌──────────────┬───────────────┬─────────────────┐
│  KPI Card    │  Info Card 1  │  Info Card 2    │
│              │               │                 │
│  112,411     │  About This   │  Available      │
│  Tickets     │  Metric       │  Breakdowns     │
│              │               │                 │
│  [Details]   │               │                 │
└──────────────┴───────────────┴─────────────────┘
```

**Content:**
- **Header:** "📞 Advocacy Capacity Planning"
- **Description:** 
  ```markdown
  **Data Source:** Z2_TICKETS (Last 90 Days)
  **Filter Logic:** `ADV_TICKET_FILTER_CAPACITY = TRUE` excludes automated resolutions and tickets that never reached a human agent.
  ```
- **Info Card 1:** Explain the metric and 90-day rolling window
- **Info Card 2:** List available breakdown dimensions (7 total)

---

## 6. Implementation Checklist

**Files to Create:**
- `services/snowflake_svc/z2_tickets/__init__.py` - Export `fetch_capacity_kpi`
- `services/snowflake_svc/z2_tickets/sql.py` - Contains BASE_CTE and CAPACITY_KPI_QUERY
- `services/snowflake_svc/z2_tickets/service.py` - Service function with `@st.cache_data`
- `metrics/definitions/z2_tickets.py` - Register `advocacy_capacity_tickets` metric
- `ui/pages/advocacy_capacity.py` - Page render function

**Files to Update:**
- `core/filter_config.py` - Add 6 filter configs (working_region, handoff_bucket, business_impact, department, experience_type, channel)
- `services/snowflake_svc/drill_down/sql.py` - Update FILTER_MAP with 7 dimensions, copy BASE_CTE from z2_tickets/sql.py
- `services/snowflake_svc/__init__.py` - Export `fetch_capacity_kpi`, `fetch_trend_data`
- `metrics/definitions/__init__.py` - Export z2_tickets module
- `metrics/loader.py` - Call `definitions.z2_tickets.register_all()`
- `ui/pages/__init__.py` - Export advocacy_capacity page (if demo was deleted)
- `streamlit_app.py` - Add advocacy_capacity page to navigation

**Critical Implementation Notes:**
1. ✅ Define BASE_CTE in `z2_tickets/sql.py` with computed REGION_BUCKET and HANDOFF_BUCKET
2. ✅ Copy EXACT same BASE_CTE to `drill_down/sql.py`
3. ✅ In `filter_config.py`, use `sql_column="REGION_BUCKET"` and `sql_column="HANDOFF_BUCKET"` (not raw columns)
4. ✅ Verify formatter aliases exist in `ui/components/formatters.py` (format_currency, format_number, format_percentage)
5. ✅ Verify `fetch_trend_data` is exported in `services/snowflake_svc/__init__.py`
6. ✅ No `st.info()` messages in `services/snowflake_svc/session.py`

---

## 7. Key Patterns Demonstrated

### Pattern 1: COALESCE for NULL Handling
```sql
COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET
```
**When to use:** >20% of records have NULL in a dimension.

### Pattern 2: CASE Statement for Bucketing
```sql
CASE
    WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0'
    WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1'
    WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2'
    WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+'
    ELSE 'Unknown'
END AS HANDOFF_BUCKET
```
**When to use:** Too many distinct values (0-10) need grouping.

### Pattern 3: Shared BASE_CTE
```python
# services/z2_tickets/sql.py
BASE_CTE = """WITH z2_capacity_data AS (...)"""
CAPACITY_KPI_QUERY = BASE_CTE + "SELECT COUNT(TICKET_ID)..."

# services/drill_down/sql.py
BASE_CTE = """WITH z2_capacity_data AS (...)"""  # EXACT COPY
BREAKDOWN_QUERY_TEMPLATE = BASE_CTE + "SELECT {dimension}..."
```
**Why:** Prevents "invalid identifier" errors when filters reference computed columns.

### Pattern 4: Monthly Aggregation for 90-Day Windows
```sql
DATE_TRUNC('MONTH', CREATED_TIMESTAMP)  -- 3 data points (not 90)
```
**Why:** Daily granularity over 90 days produces too many data points (90 bars on a chart).

---

## 8. Common Mistakes to Avoid

### ❌ Mistake 1: Mismatched Filter Column References
**Wrong:**
```python
# filter_config.py
FilterConfig(
    sql_column="TICKET_ASSIGNEE_STATIONS",  # Raw column doesn't exist in BASE_CTE!
    ...
)
```

**Right:**
```python
# filter_config.py
FilterConfig(
    sql_column="HANDOFF_BUCKET",  # Computed alias from BASE_CTE ✓
    ...
)
```

### ❌ Mistake 2: Incorrect Business Impact Values
**Wrong:**
```python
options=["1 - Critical", "2 - Major", ...]  # With dash
```

**Right:**
```python
options=["1 Critical", "2 Major", ...]  # With space ✓
```

### ❌ Mistake 3: Including Agent Group in Sidebar Filters
**Wrong:**
```python
available_filters=[..., "agent_group"]  # 50+ options crashes UX
```

**Right:**
```python
# Exclude from sidebar filters, keep in breakdown dimensions only
available_filters=[...] # No agent_group
FILTER_MAP = {..., "Agent Group": "AGENT_GROUP_NAME"}  # Include in breakdowns ✓
```

### ❌ Mistake 4: Forgetting to Copy BASE_CTE to drill_down/sql.py
**Wrong:**
```python
# z2_tickets/sql.py has BASE_CTE
# drill_down/sql.py has different CTE or no CTE
```

**Right:**
```python
# Both files have EXACT SAME BASE_CTE ✓
```

---

## 9. Validation Queries Summary

Run these queries with Snow CLI BEFORE generating code:

**Main KPI:**
```bash
snow sql -q "SELECT COUNT(TICKET_ID) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) AND CREATED_TIMESTAMP < CURRENT_DATE()"
```
Expected: ~112,411

**All Dimensions:**
```bash
# Working Region
snow sql -q "SELECT COALESCE(AGYLE_WORKING_REGION, 'Unknown') AS REGION_BUCKET, COUNT(*) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) GROUP BY REGION_BUCKET ORDER BY COUNT(*) DESC"

# Handoffs
snow sql -q "SELECT CASE WHEN TICKET_ASSIGNEE_STATIONS = 0 THEN '0' WHEN TICKET_ASSIGNEE_STATIONS = 1 THEN '1' WHEN TICKET_ASSIGNEE_STATIONS = 2 THEN '2' WHEN TICKET_ASSIGNEE_STATIONS >= 3 THEN '3+' END AS HANDOFF_BUCKET, COUNT(*) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) GROUP BY HANDOFF_BUCKET ORDER BY COUNT(*) DESC"

# Business Impact
snow sql -q "SELECT BUSINESS_IMPACT, COUNT(*) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) GROUP BY BUSINESS_IMPACT ORDER BY COUNT(*) DESC"

# Department
snow sql -q "SELECT DEPARTMENT, COUNT(*) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) GROUP BY DEPARTMENT ORDER BY COUNT(*) DESC"
```

**Trend Data:**
```bash
snow sql -q "SELECT DATE_TRUNC('MONTH', CREATED_TIMESTAMP) AS PERIOD, COUNT(TICKET_ID) FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS WHERE ADV_TICKET_FILTER_CAPACITY = TRUE AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE()) GROUP BY PERIOD ORDER BY PERIOD ASC"
```
Expected: 3 rows (3 months)

---

**End of Brief**

This example demonstrates all POC 3 learnings:
- ✅ 90-day window (not 7-day)
- ✅ Unified "Dimensions" section (filters + breakdowns)
- ✅ COALESCE pattern for NULL handling
- ✅ CASE statement pattern with computed aliases
- ✅ BASE_CTE shared across all queries
- ✅ No target (count-only metric)
- ✅ Monthly trend aggregation
- ✅ Actual validated values (112,411 tickets)
- ✅ Sections 6, 7, 9, 10 removed (Claude handles these)
