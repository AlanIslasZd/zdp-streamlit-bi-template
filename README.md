# ZDP Streamlit BI Template

**A production-ready Streamlit template for building enterprise analytics dashboards with Claude Code.**

This template provides the architecture, components, and AI-assisted workflow to help data analysts create professional dashboards in hours, not weeks.

---

## 🎯 What This Template Provides

### For Analysts
- **Dashboard Brief Template** - Fill out a form, let Claude generate your dashboard
- **Onboarding Guide** - Step-by-step instructions to create your first dashboard
- **Working Example** - Z2 Tickets reference implementation with real SQL
- **Mock Data Support** - Develop locally without Snowflake access

### For Dashboards
- **Layered Architecture** - Clean separation: Core → Services → Metrics → UI
- **Metric Registry** - Define metrics once, reuse everywhere (no parameter hell)
- **Drill-Down Modals** - Interactive breakdowns with attainment coloring
- **Global Filters** - Sidebar filters that affect all metrics
- **Smart Caching** - `@st.cache_data` for optimal performance

### For Claude Code
- **CLAUDE.md** - AI guardrails that enforce architectural patterns
- **"Fail Loud" Rule** - Claude asks questions instead of guessing
- **Structured Brief** - Pre-generation checklist prevents common errors

---

## 🚀 Quick Start: See the Demo (2 Minutes)

```bash
git clone https://github.com/zendesk/zdp-streamlit-bi-template.git
cd zdp-streamlit-bi-template
pip install -e .
streamlit run streamlit_app.py
```

**You'll see:**
- Demo Revenue card with gauge chart, target, and YoY
- Filters in the sidebar (Region, Segment)
- "Details" button → Drill-down modal
- Breakdown by dimension with color-coded bars

**No Snowflake required!** The demo runs with mock data.

---

## 📚 Create Your Own Dashboard

### 🏃 Fast Track (30 Minutes)
**For simple dashboards (just a count/sum, no frills):**

1. **Test your SQL** - Run your query in Snow CLI
2. **Fill the brief** - Copy `docs/DASHBOARD_BRIEF_QUICK_START.md` (takes 15 min)
3. **Generate** - Paste prompt into Claude Code
4. **Launch** - `streamlit run streamlit_app.py`

**Start here:** [`docs/QUICK_START.md`](docs/QUICK_START.md) ← **NEW!**

---

### 🎯 Full Experience (2-3 Hours)
**For complex dashboards (targets, filters, drill-downs, trend charts):**

**Step 1: Prepare Your Data (30 min)**
1. Identify your Snowflake table
2. Write and test your SQL queries with Snow CLI
3. Check available columns: `snow sql -q "SHOW COLUMNS IN your_table"`

**Step 2: Fill Out the Brief (45 min)**
```bash
cp docs/DASHBOARD_BRIEF_TEMPLATE.md MY_DASHBOARD_BRIEF.md
# Fill in: Data source, KPIs, filters, drill-downs, SQL queries
```

**Key questions in the brief:**
- **Has Target? [YES | NO]** - Determines if gauge chart shows
- **Has YoY? [YES | NO]** - Adds year-over-year comparison
- **Has Global Filters? [YES | NO]** - Sidebar filters
- **Has Drill-Downs? [YES | NO]** - "Details" button with breakdowns

**Step 3: Generate with Claude (30 min)**
1. Open fresh Claude Code session
2. Paste the execution prompt (see `docs/ONBOARDING_GUIDE.md`)
3. Provide your filled brief
4. Claude generates the dashboard following the template architecture

**Step 4: Validate (30 min)**
1. Test imports: `python -c "from services.snowflake_svc import my_service"`
2. Run with mock data: `USE_MOCK_DATA=True`
3. Run with real data: `USE_MOCK_DATA=False`
4. Check validation checklist in generated README

**Full walkthrough:** [`docs/ONBOARDING_GUIDE.md`](docs/ONBOARDING_GUIDE.md)

---

## 📂 Architecture

```
4-Layer Architecture:

┌─────────────────────────────────────┐
│  UI Layer (ui/)                     │
│  Pages orchestrate, components      │
│  render via registry lookup         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Metrics Layer (metrics/)           │
│  Registry: register once, reuse     │
│  everywhere. Eliminates wiring bugs │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Service Layer (services/)          │
│  SQL queries + caching. Mock data   │
│  fallback for local development     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Core Layer (core/)                 │
│  SessionManager for filters, config │
│  constants, shared utilities        │
└─────────────────────────────────────┘
```

**Why this architecture?**
- **Testable** - Each layer can be tested independently
- **Scalable** - Add metrics without changing components
- **Maintainable** - SQL in services, not UI
- **Reusable** - Components work for any metric

---

## 📖 Documentation

| File | Purpose | Start Here? |
|------|---------|-------------|
| **[QUICK_START.md](docs/QUICK_START.md)** 🆕 | Build your first dashboard in 30 minutes | ✅ START HERE |
| **[ONBOARDING_GUIDE.md](docs/ONBOARDING_GUIDE.md)** | Full walkthrough for complex dashboards | ✅ If you need filters/drill-downs |
| **[DASHBOARD_BRIEF_QUICK_START.md](docs/DASHBOARD_BRIEF_QUICK_START.md)** 🆕 | Simple brief (30 min) | ✅ For simple KPIs |
| **[DASHBOARD_BRIEF_TEMPLATE.md](docs/DASHBOARD_BRIEF_TEMPLATE.md)** | Full brief (45 min) | ✅ For complex dashboards |
| **[DASHBOARD_BRIEF_EXAMPLE_Z2.md](docs/DASHBOARD_BRIEF_EXAMPLE_Z2.md)** | Z2 Tickets reference example | ℹ️ Reference |
| **[CLAUDE.md](CLAUDE.md)** | AI guardrails for code generation | ℹ️ Claude reads this |
| **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** | Common issues & solutions | 🆘 When stuck |

---

## 🎓 Example: Z2 Tickets Dashboard

**The template includes a complete reference implementation:**

**Data:** `FUNCTIONAL.CUSTOMER_EXPERIENCE.Z2_TICKETS`  
**Metric:** Advocacy Capacity Tickets (last 7 days)  
**Filters:** Working Region, Handoffs, Business Impact  
**Drill-Downs:** Agent Group, Department, Experience Type, Channel

**See the brief:** `docs/DASHBOARD_BRIEF_EXAMPLE_Z2.md`  
**Validated SQL:** All queries tested with Snow CLI

This example shows:
- ✅ How to write a complete brief
- ✅ How to handle global filters
- ✅ How to configure drill-downs
- ✅ Real Snowflake SQL that works

---

## 🔥 Key Features

### 1. Metric Registry Pattern
**No more parameter hell!**

❌ **Before (Traditional):**
```python
render_card(
    title="Revenue",
    value=1_250_000,
    target=1_200_000,
    format="currency",
    show_gauge=True,
    show_yoy=True,
    ...  # 10 more parameters
)
```

✅ **After (Registry):**
```python
render_donut_card("revenue", where_sql)
```

All configuration lives in one place (`metrics/definitions/`), components just look it up.

### 2. Flexible Target Handling
**Not all metrics have targets!**

The template handles both:
- **With Target:** Gauge chart + delta + attainment colors
- **Without Target:** Just the value (clean, simple)

Specify in your brief: **"Has Target? [YES | NO]"**

### 3. AI-Assisted Generation
**Claude follows strict rules:**
- ✅ Uses your EXACT SQL (no guessing)
- ✅ Asks questions when brief is incomplete
- ✅ Follows 4-layer architecture
- ✅ Generates validation checklist

**CLAUDE.md** enforces these rules automatically.

### 4. Mock Data for Development
**Work without Snowflake:**
```python
USE_MOCK_DATA = True  # Local development
USE_MOCK_DATA = False # Production
```

Every service provides realistic mock data for testing.

---

## 🛠 Technical Stack

- **Python 3.8+**
- **Streamlit ≥1.40.0** (Streamlit in Snowflake compatible)
- **Snowflake Snowpark** (for production)
- **Altair** (drill-down charts)
- **Plotly** (gauge charts)

---

## 🤝 Contributing

This template is maintained by the ZDP BI Team.

**Want to improve it?**
1. Create a branch
2. Make your changes
3. Test with a POC dashboard
4. Submit a PR

**Questions?** Ask in `#zdp-bi-team` on Slack.

---

## 📦 What's Included

```
zdp-streamlit-bi-template/
├── CLAUDE.md                       # AI guardrails
├── README.md                       # This file
├── streamlit_app.py                # Entry point
├── pyproject.toml                  # Dependencies
├── core/                           # Config + state
├── services/snowflake_svc/         # Data access
│   ├── demo/                       # Demo service
│   └── drill_down/                 # Breakdown queries
├── metrics/                        # Registry + definitions
│   ├── metric.py                   # Metric dataclass
│   ├── registry.py                 # Registry pattern
│   └── definitions/demo.py         # Demo metric
├── ui/                             # Components + pages
│   ├── components/                 # Reusable UI
│   │   ├── donut_card.py          # Metric card
│   │   ├── drill_modal_v2.py      # Modal
│   │   ├── drill_tabs/            # Breakdown tab
│   │   ├── filters.py             # Filter sidebar
│   │   └── theme.py               # Dark theme
│   └── pages/demo.py              # Demo page
└── docs/                          # Documentation
    ├── ONBOARDING_GUIDE.md        # ← Start here
    ├── DASHBOARD_BRIEF_TEMPLATE.md
    ├── DASHBOARD_BRIEF_EXAMPLE_Z2.md
    ├── TROUBLESHOOTING.md
    └── HOW_TO_CUSTOMIZE.md
```

---

## 🎯 Success Stories

**What you can build with this template:**
- ✅ Advocacy Capacity Planning (Z2 Tickets)
- ✅ Revenue Dashboards with targets
- ✅ Operational Metrics without targets
- ✅ Drill-down analysis by any dimension
- ✅ Multi-page analytics apps

**Time to first dashboard:** 2-3 hours (with Claude Code)  
**Time to second dashboard:** 1 hour (you know the pattern)

---

## 🚀 Next Steps

1. **Try the demo:** `streamlit run streamlit_app.py`
2. **Read the onboarding guide:** `docs/ONBOARDING_GUIDE.md`
3. **Fill out a brief:** `docs/DASHBOARD_BRIEF_TEMPLATE.md`
4. **Generate your dashboard** with Claude Code
5. **Share with your team!**

---

## 📄 License

Internal Zendesk use only.

---

## 🙋 Getting Help

**Stuck?**
- Check `docs/TROUBLESHOOTING.md` first
- Review `docs/DASHBOARD_BRIEF_EXAMPLE_Z2.md` for reference
- Read `CLAUDE.md` to understand Claude's rules
- Ask in `#zdp-bi-team` Slack

**Have a question about the template?**  
Tag @alan in #zdp-bi-team

---

**Built with ❤️ by the ZDP BI Team**
