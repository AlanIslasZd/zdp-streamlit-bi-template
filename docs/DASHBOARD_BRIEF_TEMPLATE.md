# Dashboard Brief Template

**Dashboard Name:** `[your-dashboard-name]`  
**Created By:** [Your Name]  
**Date:** [YYYY-MM-DD]

---

## 0. Quick Decision Tree

Answer these to determine if you need this full template:

1. [ ] My metric has a target (gauge chart, attainment %)
2. [ ] My metric has year-over-year comparison
3. [ ] My dashboard has global filters (sidebar)
4. [ ] My dashboard has drill-down dimensions (Details modal)
5. [ ] My dashboard has a trend chart (time-series)

**If you checked 0-1 boxes:** Use [`DASHBOARD_BRIEF_QUICK_START.md`](./DASHBOARD_BRIEF_QUICK_START.md) instead (30 min)  
**If you checked 2+ boxes:** Continue with this full template (45 min)

---

## 💡 Pro-Tip: You're the Zendesk Expert, Claude is the Python Expert

**The secret to fast dashboard generation:** Provide working SQL queries, and Claude will wire everything up perfectly.

### What You Need to Do:
1. **Test your SQL in Snow CLI first** - Make sure it returns the data you expect.
2. **Write normal SQL** - No need to write complex CTEs or type-casting. Just write standard `SELECT` statements. 
3. **Want to group numbers into buckets?** (e.g., grouping ticket stations into "0", "1", "2", "3+"). Just describe it in plain English in Section 2. Claude will autonomously write and test the bucketed SQL for you.

---

## 1. Data Source

**Table:** `[SCHEMA.DATABASE.TABLE_NAME]`

**Business Filter (Applied to ALL queries):**
```sql
WHERE [your_business_filter_logic]
  AND [date_filter_logic]
```

**Time Window:** Select one and update SQL above:
- [ ] 7-day rolling
- [ ] 30-day rolling
- [ ] 90-day rolling
- [ ] MTD (Month-to-Date)
- [ ] QTD (Quarter-to-Date)
- [ ] YTD (Year-to-Date)
- [ ] Custom: `___________________`

---

## 2. Dimensions (Used for BOTH Filters and Breakdowns)

**IMPORTANT:** List ALL dimensions you want to analyze by. Each dimension will automatically be available as both a sidebar filter AND a breakdown dimension.

**Rule of Thumb:** If a dimension has more than 20 distinct values (like Agent Name), it will only be used as a breakdown, not a sidebar filter.

---

### Dimension 1: [Name]

- **SQL Column:** `[RAW_COLUMN_NAME]`  
  *(If you need NULLs converted to 'Unknown', just mention it here: e.g., "Use COALESCE to make NULLs 'Unknown'")*

- **Values:** `["Value1", "Value2", "Value3", ...]`

- **Include in Sidebar Filter?** [ ] YES [ ] NO (Reason: _________________)

- **Include in Breakdown?** [ ] YES [ ] NO

---

### Dimension 2: [Name]

- **SQL Column:** `[RAW_COLUMN_NAME]`  
  *(If you want Claude to bucket numeric values, explain the buckets here: e.g., "Group values into 0, 1, 2, and 3+")*

- **Values:** `["Value1", "Value2", ...]`

- **Include in Sidebar Filter?** [ ] YES [ ] NO

- **Include in Breakdown?** [ ] YES [ ] NO

---

### [Add more dimensions as needed]

---

## 3. Main KPI (Scorecard)

### Scorecard 1: [Metric Name]

**Metric Key:** `[metric_key_lowercase_underscores]`

**SQL Query:**

**Just write your normal SQL query!** Claude will restructure it if needed (e.g., adding BASE_CTE logic for your computed dimensions).

```sql
SELECT
    [aggregation] AS [ACTUAL_COLUMN_NAME]
FROM [TABLE_NAME]
WHERE [business_filter_logic]
  AND [date_filter_logic]
```

**Expected Result:** [e.g., "~8,375 tickets" or "$1.2M revenue"]

**Configuration:**
- **Format:** [ ] Number [ ] Currency [ ] Percentage
- **Actual Column:** `[ACTUAL_COLUMN_NAME]`
- **Has Target?** [ ] YES [ ] NO  
  - If YES: Provide Target Column name and Threshold logic (e.g., Green ≥100%)
- **Has YoY?** [ ] YES [ ] NO  
  - If YES: Provide the Last Year Column name

---

## 4. Drill-Down Configuration

### 4.1 Breakdown Tab

**Does this dashboard have drill-downs?** [ ] YES [ ] NO

If YES:

**Available Dimensions:** List the dimension names from Section 2 that should appear in the "Break down by:" dropdown.

- [ ] [Dimension 1 name]
- [ ] [Dimension 2 name]

**✨ Built-In Feature: CSV Export**

Your dashboard automatically includes click-to-export functionality! Users can:
1. Click "💾 Export by Slice" (collapsible section below the chart)
2. Expand any dimension value (e.g., "AMER: 6,200 records")
3. Click "📥 Export" to download a CSV with just those records
4. The CSV includes all columns and respects all active filters

*No configuration needed - this feature is built into the template!*

---

### 4.2 Trend Tab (Optional)

**Does this metric need a Trend tab?** [ ] YES [ ] NO  
*(A time-series line chart showing how the metric changes over time)*

If YES:

- **Date Column for X-Axis:** `[SQL_COLUMN_NAME]`
- **Default Granularity:** [ ] Daily [ ] Weekly [ ] Monthly

---

## 5. Page Layout

### Page 1: [Page Name]

**File:** `ui/pages/[page_name].py`

**URL Path:** `/[page-url-path]`

**Sidebar Filters:** List filter IDs from Section 2 that should appear in the sidebar.

```python
available_filters=[
    "[filter_id_1]",
    "[filter_id_2]",
]
```

**Header Content:**
- **Header:** "[Page Title]"
- **Description:** [Brief explanation of what this page shows]

---

**End of Template**

---

## Next Steps

Provide this brief to Claude with the prompt:

```
I want to build a new dashboard from the attached brief.

**Step 1:** Clone the master template from [YOUR_TEMPLATE_PATH] to a new directory called [NEW_DASHBOARD_NAME].
**Step 2:** cd into the new directory and read CLAUDE.md.
**Step 3:** 🚨 CRITICAL HOLD: Before writing any code, execute the PRE-GENERATION CHECKLIST located at the bottom of CLAUDE.md. If it fails, STOP and tell me what is missing.
**Step 4:** If the checklist passes, generate the dashboard exactly as instructed in CLAUDE.md.
```
