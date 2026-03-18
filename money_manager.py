import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import calendar
import plotly.graph_objects as go
import plotly.express as px

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Paisa Manager 💸",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

:root {
    --bg: #0d0d0d;
    --surface: #161616;
    --surface2: #1f1f1f;
    --surface3: #282828;
    --gold: #f5c542;
    --gold2: #e8a900;
    --green: #22c55e;
    --red: #ef4444;
    --blue: #38bdf8;
    --orange: #fb923c;
    --text: #f0f0f0;
    --muted: #6b6b6b;
    --border: #252525;
}

.stApp { background: var(--bg) !important; font-family: 'DM Sans', sans-serif !important; }
.stApp > header { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; }

/* Buttons */
.stButton > button {
    background: var(--gold) !important; color: #000 !important;
    border: none !important; border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.03em !important; transition: all 0.15s ease !important;
}
.stButton > button:hover { background: var(--gold2) !important; transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(245,197,66,0.3) !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}
.stSelectbox [data-baseweb="select"] > div { background: var(--surface2) !important; border-color: var(--border) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; border-radius: 7px !important; color: var(--muted) !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.85rem !important; }
.stTabs [aria-selected="true"] { background: var(--gold) !important; color: #000 !important; }

/* Metrics */
div[data-testid="metric-container"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 1rem !important; }
div[data-testid="metric-container"] label { color: var(--muted) !important; font-size: 0.75rem !important; }

h1 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 0.05em !important; font-size: 3rem !important; color: var(--gold) !important; margin-bottom: 0 !important; }
h2 { font-family: 'Bebas Neue', sans-serif !important; color: var(--text) !important; letter-spacing: 0.05em !important; }
h3 { font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; color: var(--muted) !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.15em; }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem; }
.card-gold { border-left: 3px solid var(--gold); }
.card-green { border-left: 3px solid var(--green); }
.card-red { border-left: 3px solid var(--red); }
.card-blue { border-left: 3px solid var(--blue); }

.tag {
    display: inline-block; padding: 2px 10px; border-radius: 99px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em;
}
.tag-food { background: rgba(251,146,60,0.15); color: #fb923c; }
.tag-outing { background: rgba(56,189,248,0.15); color: #38bdf8; }
.tag-shopping { background: rgba(167,139,250,0.15); color: #a78bfa; }
.tag-recharge { background: rgba(34,197,94,0.15); color: #22c55e; }
.tag-other { background: rgba(107,107,107,0.15); color: #9ca3af; }
.tag-income { background: rgba(245,197,66,0.15); color: #f5c542; }

.tx-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 1rem; border-radius: 10px;
    background: var(--surface2); margin-bottom: 0.4rem;
    border: 1px solid var(--border); transition: border-color 0.15s;
}
.tx-row:hover { border-color: var(--gold); }
.tx-amount-exp { color: var(--red); font-weight: 700; font-size: 1rem; }
.tx-amount-inc { color: var(--green); font-weight: 700; font-size: 1rem; }

.budget-bar-bg { background: var(--surface3); border-radius: 99px; height: 10px; overflow: hidden; margin: 6px 0 2px; }
.alert-box {
    padding: 0.75rem 1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
    margin-bottom: 0.5rem;
}
.alert-danger { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }
.alert-warn { background: rgba(245,197,66,0.1); border: 1px solid rgba(245,197,66,0.3); color: #f5c542; }
.alert-good { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: #22c55e; }
</style>
""", unsafe_allow_html=True)

# ─── Data ──────────────────────────────────────────────────────────────────────
DATA_FILE = "money_data.json"

CATEGORIES = {
    "🍔 Food / Canteen": "food",
    "🎉 Friends Outing": "outing",
    "👕 Shopping / Clothes": "shopping",
    "📱 Recharge / Internet": "recharge",
    "📦 Other": "other",
}

CAT_COLORS = {
    "food": "#fb923c", "outing": "#38bdf8",
    "shopping": "#a78bfa", "recharge": "#22c55e", "other": "#6b7280",
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {
        "pocket_money": 3500,
        "transactions": [],
        "savings_goal": 500,
        "budgets": {"food": 1000, "outing": 700, "shopping": 500, "recharge": 300, "other": 300},
    }

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

D = st.session_state.data

# ─── Helpers ───────────────────────────────────────────────────────────────────
def get_month_txns(year, month):
    return [t for t in D["transactions"]
            if t["date"].startswith(f"{year}-{str(month).zfill(2)}")]

def month_spent(year, month):
    return sum(t["amount"] for t in get_month_txns(year, month) if t["type"] == "expense")

def month_earned(year, month):
    return sum(t["amount"] for t in get_month_txns(year, month) if t["type"] == "income")

def cat_tag(cat):
    return f'<span class="tag tag-{cat}">{cat.upper()}</span>'

def spending_tip(pct):
    if pct >= 100: return "🚨 Budget khatam! Ruk bhai!", "alert-danger"
    elif pct >= 80: return "⚠️ 80% kharcha ho gaya, sambhal!", "alert-warn"
    elif pct >= 60: return "👀 Thoda zyada ho raha hai...", "alert-warn"
    else: return "✅ Badhiya chal raha hai!", "alert-good"

now = date.today()
cur_year, cur_month = now.year, now.month

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💸 Paisa Manager")
    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    new_pm = st.number_input("Monthly Pocket Money (₹)", value=D["pocket_money"], step=100, min_value=0)
    new_goal = st.number_input("Savings Goal (₹)", value=D["savings_goal"], step=100, min_value=0)
    if st.button("Save Settings", use_container_width=True):
        D["pocket_money"] = new_pm
        D["savings_goal"] = new_goal
        save_data(D)
        st.success("Saved! ✅")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Category Budgets (₹)")
    new_budgets = {}
    for cat_label, cat_key in CATEGORIES.items():
        if cat_key != "other":
            new_budgets[cat_key] = st.number_input(cat_label, value=D["budgets"].get(cat_key, 300), step=50, min_value=0, key=f"bud_{cat_key}")
    new_budgets["other"] = D["budgets"].get("other", 300)

    if st.button("Update Budgets", use_container_width=True):
        D["budgets"] = new_budgets
        save_data(D)
        st.success("Budgets update ho gaye! ✅")
        st.rerun()

    st.markdown("---")
    st.caption("Tera paisa, teri zimmedari 💪")

# ─── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 💸 PAISA MANAGER")
st.markdown(f"<div style='color:#6b6b6b;font-size:0.85rem;margin-bottom:1rem'>{now.strftime('%A, %d %B %Y')} &nbsp;|&nbsp; Pocket Money: ₹{D['pocket_money']:,}/month</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "➕ Add Transaction", "📊 Monthly Report", "💰 Savings"])

# ══════════════════════════════════════════════════════════
# TAB 1 — Dashboard
# ══════════════════════════════════════════════════════════
with tab1:
    spent = month_spent(cur_year, cur_month)
    earned = month_earned(cur_year, cur_month)
    total_budget = D["pocket_money"] + earned
    remaining = total_budget - spent
    saved_so_far = remaining  # what's left = potential savings
    spend_pct = int((spent / total_budget * 100)) if total_budget > 0 else 0

    # Top KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💼 Total Budget", f"₹{total_budget:,}", delta=f"+₹{earned:,} extra income" if earned else None)
    with c2:
        st.metric("💸 Kharch Hua", f"₹{spent:,}", delta=f"-{spend_pct}%", delta_color="inverse")
    with c3:
        color = "normal" if remaining >= 0 else "inverse"
        st.metric("🤑 Bacha Hai", f"₹{remaining:,}")
    with c4:
        days_left = (date(cur_year, cur_month, calendar.monthrange(cur_year, cur_month)[1]) - now).days
        st.metric("📅 Din Bache", f"{days_left} din")

    st.markdown("")

    # Main spending bar
    bar_color = "#ef4444" if spend_pct >= 90 else "#f5c542" if spend_pct >= 70 else "#22c55e"
    tip_msg, tip_cls = spending_tip(spend_pct)
    st.markdown(f'<div class="alert-box {tip_cls}">{tip_msg}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;font-size:0.8rem;color:#6b6b6b;margin-bottom:4px'>
        <span>₹0</span><span>Kharcha: ₹{spent:,} / ₹{total_budget:,}</span>
    </div>
    <div class='budget-bar-bg'>
        <div style='background:{bar_color};height:100%;width:{min(spend_pct,100)}%;border-radius:99px;
            transition:width 0.5s;box-shadow:0 0 10px {bar_color}66'></div>
    </div>
    <div style='text-align:right;font-size:0.75rem;color:#6b6b6b;margin-bottom:1rem'>{spend_pct}% used</div>
    """, unsafe_allow_html=True)

    # Per-day budget alert
    if days_left > 0 and remaining > 0:
        per_day = remaining / days_left
        st.markdown(f"""
        <div class='card card-gold' style='padding:1rem'>
            <div style='font-size:0.75rem;color:#6b6b6b;text-transform:uppercase;letter-spacing:0.1em'>Aaj ke liye budget</div>
            <div style='font-size:2rem;font-family:"Bebas Neue";color:#f5c542'>₹{per_day:.0f} <span style='font-size:1rem;color:#6b6b6b'>/ din</span></div>
            <div style='font-size:0.8rem;color:#6b6b6b'>Isse zyada mat kharch karna bhai 🙏</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Category budget progress
    st.markdown("### Category-wise Budget")
    cat_txns = {k: 0 for k in CATEGORIES.values()}
    for t in get_month_txns(cur_year, cur_month):
        if t["type"] == "expense" and t["category"] in cat_txns:
            cat_txns[t["category"]] += t["amount"]

    cols = st.columns(2)
    cat_items = [(label, key) for label, key in CATEGORIES.items()]
    for i, (label, key) in enumerate(cat_items):
        budget = D["budgets"].get(key, 0)
        used = cat_txns.get(key, 0)
        pct = int(used / budget * 100) if budget > 0 else 0
        bc = "#ef4444" if pct >= 90 else "#f5c542" if pct >= 70 else CAT_COLORS.get(key, "#6b6b6b")
        with cols[i % 2]:
            st.markdown(f"""
            <div class='card' style='padding:0.9rem 1.1rem;margin-bottom:0.5rem'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <span style='font-size:0.9rem;font-weight:600'>{label}</span>
                    <span style='font-size:0.8rem;color:#6b6b6b'>₹{used:,} / ₹{budget:,}</span>
                </div>
                <div class='budget-bar-bg' style='margin:6px 0 0'>
                    <div style='background:{bc};height:100%;width:{min(pct,100)}%;border-radius:99px'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recent transactions
    st.markdown("### Haali Transactions")
    recent = sorted(D["transactions"], key=lambda x: x["date"], reverse=True)[:8]
    if not recent:
        st.markdown("<div class='card' style='text-align:center;padding:2rem;color:#6b6b6b'>Abhi koi transaction nahi hai! Neeche add karo.</div>", unsafe_allow_html=True)
    else:
        for t in recent:
            is_inc = t["type"] == "income"
            amt_cls = "tx-amount-inc" if is_inc else "tx-amount-exp"
            sign = "+" if is_inc else "-"
            cat = t.get("category", "other")
            tag_cls = "tag-income" if is_inc else f"tag-{cat}"
            tag_text = "INCOME" if is_inc else cat.upper()
            st.markdown(f"""
            <div class='tx-row'>
                <div>
                    <div style='font-weight:600;font-size:0.95rem'>{t.get("note","") or "—"}</div>
                    <div style='display:flex;gap:6px;margin-top:3px'>
                        <span class='tag {tag_cls}'>{tag_text}</span>
                        <span style='font-size:0.72rem;color:#6b6b6b'>{t["date"]}</span>
                    </div>
                </div>
                <span class='{amt_cls}'>{sign}₹{t["amount"]:,}</span>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — Add Transaction
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Kya karna hai?")
    tx_type = st.radio("", ["💸 Expense (Kharcha)", "💰 Income (Kamaai)"], horizontal=True, label_visibility="collapsed")
    is_expense = "Expense" in tx_type

    col_a, col_b = st.columns(2)
    with col_a:
        tx_amount = st.number_input("Amount (₹)", min_value=1, max_value=50000, step=1, value=50)
    with col_b:
        tx_date = st.date_input("Date", value=date.today())

    if is_expense:
        tx_cat = st.selectbox("Category", list(CATEGORIES.keys()))
        cat_key = CATEGORIES[tx_cat]
    else:
        tx_src = st.text_input("Income source", placeholder="e.g. Freelance kaam, gift, etc.")
        cat_key = "income"

    tx_note = st.text_input("Note (optional)", placeholder="e.g. Domino's ke saath 2 log...")

    if st.button("✅ Add Karo", use_container_width=True):
        entry = {
            "id": len(D["transactions"]) + 1,
            "type": "expense" if is_expense else "income",
            "amount": tx_amount,
            "category": cat_key if is_expense else "income",
            "note": tx_note or (tx_src if not is_expense else ""),
            "date": tx_date.isoformat(),
        }
        D["transactions"].append(entry)
        save_data(D)
        st.success(f"{'Kharcha' if is_expense else 'Income'} add ho gaya — ₹{tx_amount:,}! 🎉")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🗑️ Transaction Hatao")
    if D["transactions"]:
        recent_labels = {
            f"[{t['date']}] {'−' if t['type']=='expense' else '+'} ₹{t['amount']} — {t.get('note','')[:30]}": t["id"]
            for t in sorted(D["transactions"], key=lambda x: x["date"], reverse=True)[:15]
        }
        sel = st.selectbox("Select transaction", ["— choose —"] + list(recent_labels.keys()))
        if st.button("Hatao ❌", use_container_width=True):
            if sel != "— choose —":
                tid = recent_labels[sel]
                D["transactions"] = [t for t in D["transactions"] if t["id"] != tid]
                save_data(D)
                st.success("Hata diya!")
                st.rerun()
    else:
        st.caption("Koi transaction nahi hai abhi.")


# ══════════════════════════════════════════════════════════
# TAB 3 — Monthly Report
# ══════════════════════════════════════════════════════════
with tab3:
    col_m, col_y = st.columns(2)
    with col_m:
        sel_month = st.selectbox("Month", list(range(1, 13)), index=cur_month - 1,
                                  format_func=lambda x: calendar.month_name[x])
    with col_y:
        sel_year = st.selectbox("Year", [cur_year - 1, cur_year], index=1)

    month_txns = get_month_txns(sel_year, sel_month)
    m_spent = month_spent(sel_year, sel_month)
    m_earned = month_earned(sel_year, sel_month)
    m_budget = D["pocket_money"] + m_earned
    m_saved = m_budget - m_spent

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("💸 Total Kharcha", f"₹{m_spent:,}")
    with c2: st.metric("💰 Extra Income", f"₹{m_earned:,}")
    with c3:
        st.metric("🤑 Bacha / Udha", f"₹{m_saved:,}", delta_color="normal" if m_saved >= 0 else "inverse")

    # Day-by-day spending chart
    num_days = calendar.monthrange(sel_year, sel_month)[1]
    daily_exp = {}
    daily_inc = {}
    for t in month_txns:
        d = int(t["date"].split("-")[2])
        if t["type"] == "expense":
            daily_exp[d] = daily_exp.get(d, 0) + t["amount"]
        else:
            daily_inc[d] = daily_inc.get(d, 0) + t["amount"]

    days = list(range(1, num_days + 1))
    exp_vals = [daily_exp.get(d, 0) for d in days]
    inc_vals = [daily_inc.get(d, 0) for d in days]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=days, y=exp_vals, name="Kharcha", marker_color="#ef4444", opacity=0.85, width=0.6))
    fig.add_trace(go.Bar(x=days, y=inc_vals, name="Income", marker_color="#22c55e", opacity=0.85, width=0.6))

    daily_budget_line = D["pocket_money"] / num_days
    fig.add_hline(y=daily_budget_line, line_dash="dot", line_color="#f5c542", line_width=1.5, opacity=0.7)
    fig.add_annotation(x=days[-1], y=daily_budget_line + 20, text="Daily limit",
                       showarrow=False, font=dict(color="#f5c542", size=10, family="DM Sans"), xanchor="right")

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        barmode='group',
        title=dict(text=f"{calendar.month_name[sel_month]} {sel_year} — Din Bhar Ka Hisaab",
                   font=dict(family='Bebas Neue', size=20, color='#f0f0f0'), x=0),
        xaxis=dict(tickfont=dict(color='#6b6b6b', family='DM Sans', size=10), showgrid=False, tickmode='linear', dtick=1),
        yaxis=dict(tickfont=dict(color='#6b6b6b', family='DM Sans'), gridcolor='rgba(37,37,37,0.8)', tickprefix="₹"),
        legend=dict(font=dict(color='#f0f0f0', family='DM Sans'), bgcolor='rgba(0,0,0,0)', x=0, y=1.1, orientation='h'),
        hoverlabel=dict(bgcolor='#161616', font_color='#f0f0f0', font_family='DM Sans', bordercolor='#252525'),
        margin=dict(l=10, r=10, t=50, b=10), height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Category pie
    col_pie, col_tips = st.columns([1, 1])
    with col_pie:
        cat_totals = {}
        for t in month_txns:
            if t["type"] == "expense":
                c = t.get("category", "other")
                cat_totals[c] = cat_totals.get(c, 0) + t["amount"]

        if cat_totals:
            labels_pie = [k for k in cat_totals]
            values_pie = [cat_totals[k] for k in labels_pie]
            display_labels = [next((l for l, v in CATEGORIES.items() if v == k), k) for k in labels_pie]
            colors_pie = [CAT_COLORS.get(k, "#6b7280") for k in labels_pie]

            fig2 = go.Figure(go.Pie(
                labels=display_labels, values=values_pie,
                hole=0.55, marker=dict(colors=colors_pie, line=dict(color='#0d0d0d', width=3)),
                textfont=dict(family='DM Sans', size=11, color='white'),
                hovertemplate="<b>%{label}</b><br>₹%{value:,}<br>%{percent}<extra></extra>",
            ))
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(font=dict(color='#f0f0f0', family='DM Sans', size=10), bgcolor='rgba(0,0,0,0)'),
                annotations=[dict(text=f"₹{m_spent:,}", x=0.5, y=0.5, font=dict(size=18, color='#f0f0f0', family='Bebas Neue'), showarrow=False)],
                margin=dict(l=0, r=0, t=10, b=10), height=280,
                title=dict(text="Kahan Gaya Paisa?", font=dict(family='Bebas Neue', size=18, color='#f0f0f0'), x=0),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown("<div class='card' style='text-align:center;padding:2rem;color:#6b6b6b'>Is mahine koi kharcha nahi dikhaya</div>", unsafe_allow_html=True)

    with col_tips:
        st.markdown("### 💡 Smart Tips")
        if cat_totals:
            biggest_cat = max(cat_totals, key=cat_totals.get)
            biggest_label = next((l for l, v in CATEGORIES.items() if v == biggest_cat), biggest_cat)
            biggest_amt = cat_totals[biggest_cat]

            tips = {
                "food": f"🍔 Tune ₹{biggest_amt:,} food pe kharch kiya! Ghar ka khaana try kar bhai.",
                "outing": f"🎉 Dosto ke saath ₹{biggest_amt:,} gaya. Next time Dutch karo!",
                "shopping": f"👕 Shopping pe ₹{biggest_amt:,} — kya sach mein zaroori tha?",
                "recharge": f"📱 Internet pe ₹{biggest_amt:,}. Cheaper plan dekh!",
                "other": f"📦 ₹{biggest_amt:,} 'other' mein gaya — track karna shuru karo!",
            }
            tip = tips.get(biggest_cat, "")
            st.markdown(f"""
            <div class='card card-gold' style='margin-bottom:0.6rem'>
                <div style='font-size:0.72rem;color:#6b6b6b;text-transform:uppercase;margin-bottom:4px'>Sabse Zyada Kharcha</div>
                <div>{tip}</div>
            </div>
            """, unsafe_allow_html=True)

        # Savings tip
        if m_saved >= D["savings_goal"]:
            st.markdown(f"<div class='card card-green'>🎉 Goal reach kar li! ₹{m_saved:,} bacha liya is mahine!</div>", unsafe_allow_html=True)
        elif m_saved > 0:
            need = D["savings_goal"] - m_saved
            st.markdown(f"<div class='card card-gold'>💪 ₹{need:,} aur bachao toh goal complete! Chal kar bhai!</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card card-red'>🚨 ₹{abs(m_saved):,} zyada kharcha ho gaya! Agli baar dhyaan rakh.</div>", unsafe_allow_html=True)

        # Spending rate
        if days_left > 0 and sel_month == cur_month and sel_year == cur_year:
            avg_per_day = m_spent / max(now.day, 1)
            projected = avg_per_day * num_days
            st.markdown(f"""
            <div class='card card-blue'>
                <div style='font-size:0.72rem;color:#6b6b6b;text-transform:uppercase'>Projected Month Total</div>
                <div style='font-size:1.5rem;font-family:"Bebas Neue";color:#38bdf8'>₹{projected:,.0f}</div>
                <div style='font-size:0.8rem;color:#6b6b6b'>Isi rate pe chala toh mahine mein itna jayega</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 4 — Savings
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🎯 Savings Goal")

    goal = D["savings_goal"]
    # Calculate cumulative savings across all months
    all_months_data = []
    for m in range(1, cur_month + 1):
        ms = month_spent(cur_year, m)
        me = month_earned(cur_year, m)
        mb = D["pocket_money"] + me
        saved = mb - ms
        all_months_data.append({
            "month": calendar.month_abbr[m],
            "saved": saved,
            "spent": ms,
            "income": me,
            "budget": mb,
        })

    total_saved_year = sum(x["saved"] for x in all_months_data)
    this_month_saved = all_months_data[-1]["saved"] if all_months_data else 0
    goal_pct = min(int(this_month_saved / goal * 100), 100) if goal > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🎯 This Month Goal", f"₹{goal:,}")
    with c2: st.metric("💰 Bacha Hai", f"₹{this_month_saved:,}")
    with c3: st.metric("📅 YTD Savings", f"₹{total_saved_year:,}")

    # Goal ring
    bar_color = "#22c55e" if goal_pct >= 100 else "#f5c542" if goal_pct >= 50 else "#ef4444"
    status_text = "🎉 Goal Complete!" if goal_pct >= 100 else f"{goal_pct}% done"
    st.markdown(f"""
    <div class='card' style='text-align:center;padding:2rem'>
        <div style='font-size:4rem;font-family:"Bebas Neue";color:{bar_color}'>{status_text}</div>
        <div style='background:#1f1f1f;border-radius:99px;height:18px;overflow:hidden;margin:1rem 0'>
            <div style='background:linear-gradient(90deg,{bar_color},{bar_color}99);height:100%;
                width:{goal_pct}%;border-radius:99px;transition:width 0.6s;
                box-shadow:0 0 15px {bar_color}55'></div>
        </div>
        <div style='color:#6b6b6b;font-size:0.85rem'>₹{this_month_saved:,} / ₹{goal:,} savings goal</div>
    </div>
    """, unsafe_allow_html=True)

    # Month-by-month savings chart
    if len(all_months_data) > 1:
        st.markdown("### 📈 Month-wise Savings (2025)")
        months_labels = [x["month"] for x in all_months_data]
        saved_vals = [x["saved"] for x in all_months_data]
        bar_colors = ["#22c55e" if v >= goal else "#ef4444" if v < 0 else "#f5c542" for v in saved_vals]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=months_labels, y=saved_vals,
            marker_color=bar_colors, marker_line_width=0,
            text=[f"₹{v:,}" for v in saved_vals],
            textposition='outside',
            textfont=dict(family='DM Sans', color='#f0f0f0', size=11),
        ))
        fig3.add_hline(y=goal, line_dash="dash", line_color="#f5c542", line_width=2)
        fig3.add_annotation(x=months_labels[-1], y=goal + 50, text=f"Goal ₹{goal:,}",
                           showarrow=False, font=dict(color="#f5c542", size=10, family="DM Sans"), xanchor="right")
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#6b6b6b', family='DM Sans'), showgrid=False),
            yaxis=dict(tickfont=dict(color='#6b6b6b'), gridcolor='rgba(37,37,37,0.6)', tickprefix="₹"),
            margin=dict(l=10, r=10, t=20, b=10), height=300,
            hoverlabel=dict(bgcolor='#161616', font_family='DM Sans', bordercolor='#252525'),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Savings tips
    st.markdown("### 🧠 Paisa Bachane Ke Tips")
    tips_list = [
        ("🍱", "Canteen ki jagah tiffin laao", "Hafte mein ₹200-300 bach sakte hain"),
        ("📵", "Bahar milne ki jagah ghar pe hosho", "Outing mein sabse zyada jaata hai"),
        ("🛒", "Shopping list banao pehle", "Impulse buying se bachoge"),
        ("💳", "Cash use karo, UPI nahi", "Cash dene mein dard hota hai, kharch kam hoga"),
        ("🎯", "50-30-20 rule try karo", "50% zaroorat, 30% chaahat, 20% savings"),
    ]
    cols_t = st.columns(2)
    for i, (emoji, title, desc) in enumerate(tips_list):
        with cols_t[i % 2]:
            st.markdown(f"""
            <div class='card' style='padding:0.9rem 1.1rem;margin-bottom:0.5rem'>
                <div style='font-size:1.5rem'>{emoji}</div>
                <div style='font-weight:700;font-size:0.9rem;margin-top:4px'>{title}</div>
                <div style='color:#6b6b6b;font-size:0.78rem;margin-top:2px'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
