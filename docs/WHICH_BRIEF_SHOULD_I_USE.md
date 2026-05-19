# Which Brief Should I Use?

**TL;DR:** Answer 5 YES/NO questions. If you have 0-1 YES answers, use Quick Start. If you have 2+ YES answers, use Full Template.

---

## The 5 Questions

1. **Does your metric have a target?** (e.g., goal, quota, budget)
   - YES → Gauge chart with attainment colors
   - NO → Just the value

2. **Do you want year-over-year comparison?** (This Year vs Last Year)
   - YES → Shows YoY% delta
   - NO → No comparison

3. **Do you want sidebar filters?** (e.g., filter by Region, Department)
   - YES → How many filters? If 3+, use Full Template
   - NO → No filters

4. **Do you want drill-down breakdowns?** (Click "Details" to see dimension breakdowns)
   - YES → How many dimensions? If 3+, use Full Template
   - NO → No drill-downs

5. **Do you want a trend chart?** (Line chart showing how metric changes over time)
   - YES → Use Full Template
   - NO → No trend

---

## Quick Decision Tree

```
Count your YES answers:

0-1 YES → Use DASHBOARD_BRIEF_QUICK_START.md (30 minutes)
2+ YES  → Use DASHBOARD_BRIEF_TEMPLATE.md (45 minutes)
```

---

## Visual Comparison

### Quick Start Brief (30 minutes)

**Best for:**
- Simple counts or sums
- Single KPI cards
- Minimal configuration

**Example Use Cases:**
- "How many tickets were created last week?"
- "What's total revenue this quarter?"
- "Count of active customers"

**What you fill out:**
```
Part 1: The Essentials (10 min)
  - Table name
  - Business filter
  - Main KPI SQL query
  - Expected value

Part 2: Configuration (10 min)
  - 5 YES/NO checkboxes

Part 3: Decision Tree (5 min)
  - Redirects to Full if needed

Part 4: Final Details (5 min)
  - Metric name, title, help text
```

**Total:** ~30 minutes

---

### Full Template Brief (45 minutes)

**Best for:**
- Complex dashboards
- Multiple filters
- Drill-down analysis
- Target tracking
- Trend analysis

**Example Use Cases:**
- "Show revenue by region with gauge chart and YoY comparison"
- "Advocacy capacity tickets with 6 filters and drill-downs by agent group"
- "Sales pipeline with monthly trend and attainment vs target"

**What you fill out:**
```
Section 0: Quick Decision Tree (5 min)
  - Already decided! (You're here because 2+ YES)

Section 1: Data Source (10 min)
  - Table, business filters, time window
  - Validation query

Section 2: Dimensions (15 min) ← NEW!
  - List ALL dimensions (filters + breakdowns)
  - For each: SQL column, values, NULL handling
  - Validation query per dimension

Section 3: Main KPI (10 min)
  - SQL query (Claude handles BASE_CTE if needed)
  - Target config (if YES to Q1)
  - YoY config (if YES to Q2)

Section 4: Drill-Down Config (10 min)
  - Breakdown dimensions (if YES to Q4)
  - Trend tab config (if YES to Q5)

Section 5: Page Layout (5 min)
  - Which filters in sidebar
  - Page title and description
```

**Total:** ~45 minutes

---

## Side-by-Side Feature Comparison

| Feature | Quick Start | Full Template |
|---------|-------------|---------------|
| **Single KPI** | ✅ YES | ✅ YES |
| **Target/Gauge** | ⚠️ Basic (YES/NO) | ✅ Full config (thresholds, colors) |
| **YoY Comparison** | ⚠️ Basic (YES/NO) | ✅ Full config (LY column) |
| **Sidebar Filters** | ❌ NO (use Full) | ✅ YES (Section 2) |
| **Drill-Downs** | ❌ NO (use Full) | ✅ YES (Section 4.1) |
| **Trend Chart** | ❌ NO (use Full) | ✅ YES (Section 4.2) |
| **COALESCE/CASE** | ❌ NO (use Full) | ✅ YES (Section 2, Claude handles BASE_CTE) |
| **Time to Fill** | 30 minutes | 45 minutes |
| **SQL Validation** | Main query only | Main + all dimensions |
| **Claude Generation** | 5 minutes | 10 minutes |

---

## Common Scenarios

### Scenario A: "I just want to see a count"
**Answer:** Quick Start  
**Time:** 30 minutes  
**Why:** No filters, no drill-downs, no target

---

### Scenario B: "I want a count, but filtered by 2 dimensions"
**Answer:** Full Template  
**Time:** 45 minutes  
**Why:** 2 filters = Section 2 (Dimensions)

---

### Scenario C: "I want revenue with a target gauge"
**Answer:** Quick Start (if no filters) OR Full Template (if filters)  
**Time:** 30 or 45 minutes  
**Why:** Quick Start supports targets via YES/NO checkbox. Full Template gives more control over thresholds.

---

### Scenario D: "I want tickets by region, with drill-downs by agent group and department"
**Answer:** Full Template  
**Time:** 45 minutes  
**Why:** 1 filter + 2 drill dimensions = Section 2 + Section 4

---

### Scenario E: "I want monthly revenue trend for the last 90 days"
**Answer:** Full Template  
**Time:** 45 minutes  
**Why:** Trend tab = Section 4.2

---

## Pro Tips

### Tip 1: Start Simple, Add Later
If unsure, start with Quick Start. You can always regenerate with Full Template if you need more features.

### Tip 2: The 2+ Rule is Your Friend
If you checked 2+ boxes in the Quick Start "Configuration" section, it's telling you to switch to Full Template. Trust the decision tree!

### Tip 3: Dimensions = Filters + Breakdowns
If you think "I want to filter by X" or "I want to break down by Y", that's a dimension. Count them:
- 0-1 dimensions → Quick Start
- 2+ dimensions → Full Template

### Tip 4: Reference the Z2 Example
If your dashboard feels similar to the Z2 Tickets example (multiple filters, drill-downs), you need the Full Template.

**Z2 Example has:**
- 6 sidebar filters
- 7 drill-down dimensions
- COALESCE for NULL handling
- CASE statement for bucketing
- 90-day rolling window

If your dashboard has 3+ of these, use Full Template.

---

## Still Unsure? Ask Yourself:

**"Can I describe my dashboard in one sentence without using the word 'AND'?"**

- YES → Quick Start  
  Example: "Count of tickets created last week."

- NO → Full Template  
  Example: "Count of tickets created last week **AND** filtered by region **AND** broken down by agent group **AND** compared to target."

---

## Next Steps

**Chose Quick Start?**
1. Go to [`DASHBOARD_BRIEF_QUICK_START.md`](./DASHBOARD_BRIEF_QUICK_START.md)
2. Copy to `MY_DASHBOARD_BRIEF.md`
3. Fill out Parts 1-4
4. See [`QUICK_START.md`](./QUICK_START.md) for execution

**Chose Full Template?**
1. Go to [`DASHBOARD_BRIEF_TEMPLATE.md`](./DASHBOARD_BRIEF_TEMPLATE.md)
2. Copy to `MY_DASHBOARD_BRIEF.md`
3. Fill out Sections 0-5
4. See [`ONBOARDING_GUIDE.md`](./ONBOARDING_GUIDE.md) for execution

---

**Remember:** The difference isn't complexity of the SQL — it's the number of dashboard features (filters, drill-downs, trends). Claude handles the SQL complexity either way!
