# Quick Start Brief (30-Minute Version)

**Use this brief when:** Your dashboard is simple (1-2 KPIs, minimal features)

**When to use the full template instead:** If you need 2+ of these: Target, YoY, Global Filters, Drill-Downs, Trend Tab

---

## Part 1: The Essentials (10 minutes)

### 1. Table Name
**Fully qualified table name:**  
`____________________________________________________________`

**Example:** `FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS`

---

### 2. Business Filter
**WHERE clause applied to ALL queries:**  
```sql
WHERE ___________________________________________________________
  AND ___________________________________________________________
```

**Example:**
```sql
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
```

---

### 3. Time Window
Select one:

- [ ] **7-day rolling** (weekly capacity view)
- [ ] **30-day rolling** (monthly snapshot)
- [ ] **90-day rolling** (quarterly view)
- [ ] **MTD** (Month-to-Date, resets monthly)
- [ ] **QTD** (Quarter-to-Date, resets quarterly)
- [ ] **YTD** (Year-to-Date, resets yearly)
- [ ] **Custom:** `___________________`

---

### 4. Main KPI SQL
**Complete query that returns your KPI:**  
```sql
SELECT 
    _______________ AS ACTUAL_VALUE
FROM _______________
WHERE _______________
```

**Example:**
```sql
SELECT 
    COUNT(TICKET_ID) AS TICKET_COUNT
FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
  AND CREATED_TIMESTAMP >= DATEADD('day', -90, CURRENT_DATE())
  AND CREATED_TIMESTAMP < CURRENT_DATE()
```

---

### 5. Expected Value (Validation)
**Run your query in Snow CLI first:**
```bash
snow sql -q "[PASTE YOUR QUERY HERE]"
```

**Expected value:** `___________________`  
**Actual value (from Snow CLI):** `___________________`

✅ **These must match before you proceed!**

---

## Part 2: Configuration (10 minutes)

Answer YES or NO to each question. If you answer YES to 2+ questions, **stop and use the full template instead.**

### 6. Has Target?
Does this metric have a target value (e.g., goal, quota)?

- [ ] **YES** → What is the target? `___________________`
- [ ] **NO** → Count-only metric (just show the value)

---

### 7. Has YoY (Year-over-Year)?
Do you want to compare this year vs last year?

- [ ] **YES** → Provide LY SQL query
- [ ] **NO** → No comparison

---

### 8. Has Global Filters?
Do you want sidebar filters (e.g., Region, Department)?

- [ ] **YES** → How many filters? `_____` → **Use full template**
- [ ] **NO** → No filters

---

### 9. Has Drill-Downs?
Do you want a "Details" button that opens a breakdown modal?

- [ ] **YES** → How many dimensions? `_____` → **Use full template**
- [ ] **NO** → No drill-downs

---

### 10. Has Trend Tab?
Do you want a time-series chart showing how the metric changes over time?

- [ ] **YES** → Date column: `___________________` → **Use full template**
- [ ] **NO** → No trend chart

---

## Part 3: Decision Tree (5 minutes)

Count how many YES answers you have in Part 2:

- **0-1 YES:** Continue below (you're in the right place)
- **2+ YES:** Stop. Use [`DASHBOARD_BRIEF_TEMPLATE.md`](./DASHBOARD_BRIEF_TEMPLATE.md) instead.

---

## Part 4: Final Details (5 minutes)

### KPI Format Type
Select one:

- [ ] **Number** (e.g., 112,411 tickets)
- [ ] **Currency** (e.g., $1.2M)
- [ ] **Percentage** (e.g., 87.3%)

---

### Metric Name
**Unique identifier for this metric:**  
`_______________________________`

**Example:** `advocacy_capacity_tickets`

---

### Metric Title
**Display name for the scorecard:**  
`_______________________________`

**Example:** "Advocacy Capacity Tickets"

---

### Help Text
**Short description (1-2 sentences):**  
```
___________________________________________________________________
___________________________________________________________________
```

**Example:**  
"Tracks tickets meeting advocacy capacity criteria over a 90-day rolling window. Excludes automated resolutions and tickets that never reached a human agent."

---

## ✅ You're Done!

**Next step:** Provide this brief to Claude with the prompt:

```
I want to build a dashboard from this Quick Start brief. 

Follow CLAUDE.md strictly. If anything is unclear, ask before generating code.

[Attach this filled-out DASHBOARD_BRIEF_QUICK_START.md file]
```

---

## Example: Completed Quick Start Brief

### Part 1: The Essentials

1. **Table Name:** `FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS`
2. **Business Filter:**
   ```sql
   WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
     AND CREATED_TIMESTAMP >= DATEADD('day', -7, CURRENT_DATE())
     AND CREATED_TIMESTAMP < CURRENT_DATE()
   ```
3. **Time Window:** ☑ 7-day rolling
4. **Main KPI SQL:**
   ```sql
   SELECT COUNT(TICKET_ID) AS TICKET_COUNT
   FROM FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS
   WHERE ADV_TICKET_FILTER_CAPACITY = TRUE
     AND CREATED_TIMESTAMP >= DATEADD('day', -7, CURRENT_DATE())
     AND CREATED_TIMESTAMP < CURRENT_DATE()
   ```
5. **Expected Value:** 16,047  
   **Actual Value:** 16,047 ✅

### Part 2: Configuration

6. **Has Target?** ☑ NO
7. **Has YoY?** ☑ NO
8. **Has Global Filters?** ☑ NO
9. **Has Drill-Downs?** ☑ NO
10. **Has Trend Tab?** ☑ NO

**Decision:** 0 YES answers → Continue with Quick Start ✅

### Part 4: Final Details

- **KPI Format Type:** ☑ Number
- **Metric Name:** `simple_ticket_count`
- **Metric Title:** "Ticket Count (Last 7 Days)"
- **Help Text:** "Total tickets meeting capacity criteria in the last 7 days."

---

## Troubleshooting

**Q: My query returns multiple rows. What do I do?**  
A: Add `LIMIT 1` to your query, or use an aggregate function like `SUM()`, `AVG()`, `COUNT()`.

**Q: My SQL query failed in Snow CLI. What now?**  
A: Fix the query until it runs successfully. Do NOT provide a broken query to Claude.

**Q: I need to filter by multiple dimensions. Can I use Quick Start?**  
A: No. If you need 2+ filters, use the [full template](./DASHBOARD_BRIEF_TEMPLATE.md).

**Q: Can I add features later (like drill-downs)?**  
A: Yes, but it's easier to include them upfront. If you know you'll need them, use the full template now.

---

**End of Quick Start Brief**
