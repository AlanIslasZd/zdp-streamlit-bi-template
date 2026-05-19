# 🚀 Quick Start: Build Your First Dashboard in 30 Minutes

**Welcome, Ellen!** You're about to build a production-ready Streamlit dashboard in 4 simple steps.

---

## What You Need

- ✅ A Snowflake table with data
- ✅ A SQL query that returns your KPI
- ✅ Claude Code CLI installed (`claude --version`)
- ✅ 30 minutes

**That's it!** No Python knowledge required. No complex data engineering.

---

## Step 1: Test Your SQL (5 minutes)

Open your terminal and run:

```bash
snow sql -q "SELECT COUNT(*) FROM your_table WHERE your_filters"
```

**Did it return a number?** Great! Copy this query - you'll need it in Step 2.

**Did it fail?** Fix the SQL until it works, then continue.

---

## Step 2: Fill Out the Brief (15 minutes)

**Download this template:**
```bash
cd [path-to-your-cloned-template]/docs/
cp DASHBOARD_BRIEF_QUICK_START.md MY_DASHBOARD_BRIEF.md
```

**Open `MY_DASHBOARD_BRIEF.md` and fill in 4 things:**

1. **Table name** (e.g., `FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS`)
2. **Your SQL query** (the one you just tested)
3. **Expected value** (the number you saw in Step 1)
4. **5 YES/NO questions** (Target? YoY? Filters? Drill-downs? Trend?)

**If you answer YES to 2+ questions:** Use [`DASHBOARD_BRIEF_TEMPLATE.md`](./DASHBOARD_BRIEF_TEMPLATE.md) instead (adds 15 minutes).

---

## Step 3: Let Claude Build It (5 minutes)

**Start a fresh Claude Code session:**
```bash
cd [your-working-directory]
claude
```

**Copy-paste this prompt:**

```
I want to build a new dashboard from the attached brief.

**Step 1:** Clone the master template from [PATH_TO_THIS_FOLDER]/zdp-streamlit-bi-template to a new directory called [MY_NEW_DASHBOARD_NAME].
**Step 2:** cd into the new directory and read CLAUDE.md.
**Step 3:** 🚨 CRITICAL: Run the PRE-GENERATION CHECKLIST at the bottom of CLAUDE.md. If it fails, tell me what's missing.
**Step 4:** If the checklist passes, generate the dashboard.

[Attach MY_DASHBOARD_BRIEF.md]
```

**Replace:**
- `[PATH_TO_THIS_FOLDER]` → Your actual path (e.g., `/Users/ellen/Documents/zdp-template`)
- `[MY_NEW_DASHBOARD_NAME]` → Your dashboard folder name (e.g., `support-tickets-dashboard`)

---

## Step 4: Launch the Dashboard (5 minutes)

```bash
cd [MY_NEW_DASHBOARD_NAME]
streamlit run streamlit_app.py
```

**See your dashboard? 🎉 You're done!**

---

## What If I Get Stuck?

### Issue: "My SQL query failed in Step 1"
**Fix:** Debug your SQL in Snow CLI until it returns data. Only then move to Step 2.

### Issue: "Claude says my brief is incomplete"
**Fix:** Answer the questions Claude asks. The PRE-GENERATION CHECKLIST catches missing info.

### Issue: "I need filters/drill-downs but used Quick Start"
**Fix:** Use [`DASHBOARD_BRIEF_TEMPLATE.md`](./DASHBOARD_BRIEF_TEMPLATE.md) instead (adds Section 2: Dimensions).

### Issue: "Dashboard launched but shows no data"
**Fix:** Check `core/config.py` - set `USE_MOCK_DATA = False` to use real Snowflake data.

---

## Advanced: What If I Need More Features?

| Feature | Which Brief? | Time |
|---------|-------------|------|
| Just a count/sum (no frills) | Quick Start | 30 min |
| 1-2 sidebar filters | Quick Start (skip to full if more) | 30 min |
| 3+ sidebar filters | Full Template | 45 min |
| Drill-down breakdowns | Full Template (Section 4) | 45 min |
| Trend chart (time-series) | Full Template (Section 4.2) | 45 min |
| Target/Gauge chart | Full Template (Section 3) | 45 min |
| Year-over-year comparison | Full Template (Section 3) | 45 min |

**Rule of thumb:** If you checked 2+ YES boxes in the Quick Start brief, switch to the Full Template.

---

## Next Steps

**After your first dashboard:**
1. Deploy to Snowflake: See [DEPLOYMENT.md](./DEPLOYMENT.md)
2. Add more metrics: Edit `metrics/definitions/` and `ui/pages/`
3. Customize styling: Edit `core/styles.py`

**Need help?** Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or ask in #zdp-bi-team Slack.

---

**Pro tip:** The template handles all the complex data engineering (BASE_CTE, filter logic, caching). You just provide the SQL!
