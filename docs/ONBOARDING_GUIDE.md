# Onboarding Guide: Building Your First Dashboard

Welcome! This guide will walk you through creating a production-ready Streamlit dashboard using the ZDP template.

---

## 🚀 Quick Start (30 Minutes)

**If this is your first dashboard, start here:**

👉 **[Go to QUICK_START.md](./QUICK_START.md)** - Simple, 4-step process for basic dashboards.

**What you'll do:**
1. Test your SQL query (5 min)
2. Fill out the brief (15 min)
3. Let Claude build it (5 min)
4. Launch your dashboard (5 min)

---

## 📚 Full Walkthrough (1 Hour)

**If you need complex features (filters, drill-downs, trends), follow this guide.**

---

### Prerequisites

- ✅ Snowflake access and Snow CLI configured (`snow --version`)
- ✅ Claude Code CLI installed (`claude --version`)
- ✅ Git installed

---

### Phase 1: Prepare Your Data (10 minutes)

**Step 1: Test your SQL query**

```bash
snow sql -q "
SELECT COUNT(*) AS MY_METRIC
FROM [YOUR_TABLE]
WHERE [YOUR_FILTERS]
"
```

**Did it return a number?** Great! That's your main KPI query.

**Did it fail?** Fix the SQL until it works, then continue.

---

### Phase 2: Fill Out the Brief (30 minutes)

**Step 1: Choose which brief to use**

Answer these 5 questions:

1. [ ] My metric has a target (gauge chart)
2. [ ] My metric has year-over-year comparison
3. [ ] My dashboard has sidebar filters
4. [ ] My dashboard has drill-down dimensions
5. [ ] My dashboard has a trend chart

**Decision:**
- **0-1 checkboxes?** Use [`DASHBOARD_BRIEF_QUICK_START.md`](./DASHBOARD_BRIEF_QUICK_START.md) (15 min)
- **2+ checkboxes?** Use [`DASHBOARD_BRIEF_TEMPLATE.md`](./DASHBOARD_BRIEF_TEMPLATE.md) (30 min)

**Not sure?** Read [`WHICH_BRIEF_SHOULD_I_USE.md`](./WHICH_BRIEF_SHOULD_I_USE.md)

**Step 2: Copy the template**

```bash
cd docs/
cp DASHBOARD_BRIEF_TEMPLATE.md MY_DASHBOARD_BRIEF.md
```

**Step 3: Fill it out**

Open `MY_DASHBOARD_BRIEF.md`:
- **Section 1:** Data source (table name, filters)
- **Section 2:** Dimensions (list them in plain English - Claude writes the SQL)
- **Section 3:** Main KPI SQL (write normal SQL, no CTEs needed)
- **Section 4:** Drill-down config (if you need it)
- **Section 5:** Page layout

**Need help?** See [`DASHBOARD_BRIEF_EXAMPLE_Z2.md`](./DASHBOARD_BRIEF_EXAMPLE_Z2.md) for a complete example.

---

### Phase 3: Generate the Dashboard (10 minutes)

**Step 1: Find your template path**

```bash
pwd
# Example: /Users/ellen/Documents/zdp-streamlit-bi-template
```

**Step 2: Start fresh Claude Code session**

```bash
cd [your-working-directory]
claude
```

**Step 3: Give Claude this prompt**

```
I want to build a new dashboard from the attached brief.

**Step 1:** Clone the master template from [YOUR_PATH_FROM_ABOVE] to a new directory called [NEW_DASHBOARD_NAME].
**Step 2:** cd into the new directory and read CLAUDE.md.
**Step 3:** 🚨 CRITICAL: Run the PRE-GENERATION CHECKLIST at the bottom of CLAUDE.md. If it fails, tell me what's missing.
**Step 4:** If the checklist passes, generate the dashboard.

[Attach MY_DASHBOARD_BRIEF.md]
```

**Replace:**
- `[YOUR_PATH_FROM_ABOVE]` → Your path from Step 1
- `[NEW_DASHBOARD_NAME]` → Your folder name (e.g., `support-tickets-dashboard`)

**Step 4: Answer Claude's questions**

Claude may ask for clarification. Answer based on your data!

---

### Phase 4: Test the Dashboard (10 minutes)

```bash
cd [NEW_DASHBOARD_NAME]

# Test imports
python -c "from services.snowflake_svc import [your_service]"

# Launch with mock data
streamlit run streamlit_app.py
```

**Expected:**
- ✅ App launches
- ✅ Mock data displays
- ✅ Filters work (if you have them)
- ✅ Drill-downs open (if you have them)

**Switch to real data:**
- Set `USE_MOCK_DATA = False` in `core/config.py`
- Relaunch: `streamlit run streamlit_app.py`

---

### Phase 5: Deploy (Optional)

```bash
git init
git add .
git commit -m "Initial dashboard"
git remote add origin [YOUR_REPO]
git push -u origin main
```

**Then in Snowflake:**
1. Go to Streamlit apps
2. Click "Create" → "From GitHub"
3. Select your repo
4. Done!

---

## 🆘 Common Issues

### "Metric not registered" error
**Fix:** Check that `metrics/loader.py` calls your metric's `register_all()`

### SQL query fails
**Fix:** Test the query in Snow CLI first. Check column names (case-sensitive!)

### Filters don't update values
**Fix:** Make sure `where_sql` is passed from `render_filters()` to your service function

### No gauge chart (expected one)
**Fix:** Check if brief said "Has Target? YES". If yes, verify `target_qtd_col` is set.

---

## 💡 Tips for Success

**DO:**
- ✅ Test SQL in Snow CLI first
- ✅ Write normal SQL (Claude handles CTEs and type casts)
- ✅ Use exact column names (case-sensitive)
- ✅ Reference [`DASHBOARD_BRIEF_EXAMPLE_Z2.md`](./DASHBOARD_BRIEF_EXAMPLE_Z2.md) if stuck

**DON'T:**
- ❌ Skip SQL testing
- ❌ Guess column names
- ❌ Write SQL in UI pages (use service layer!)
- ❌ Forget to specify "Has Target? YES/NO"

---

## 📖 Next Steps

**After your first dashboard:**
1. Add more metrics to the same dashboard
2. Create a second dashboard (takes < 30 min now!)
3. Share with your team
4. Check [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for advanced topics

---

## 🙋 Getting Help

**Stuck?**
- Check [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md)
- Review [`DASHBOARD_BRIEF_EXAMPLE_Z2.md`](./DASHBOARD_BRIEF_EXAMPLE_Z2.md)
- Ask in #zdp-bi-team Slack

**Questions about features?**
- Read [`WHICH_BRIEF_SHOULD_I_USE.md`](./WHICH_BRIEF_SHOULD_I_USE.md)
- Check [`QUICK_START.md`](./QUICK_START.md) for simple path

---

## ✅ Ready to Start?

- [ ] I know my Snowflake table name
- [ ] I've tested my SQL query
- [ ] I know if my metric has a target (YES/NO)
- [ ] I've chosen which brief to use
- [ ] I have 30-60 minutes

**All checked? Let's go! Start with Phase 1. 🚀**
