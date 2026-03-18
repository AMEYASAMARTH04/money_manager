import streamlit as st
import hashlib
import calendar
from datetime import date, timedelta
from supabase import create_client, Client

# ─── Supabase Init ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

sb = get_supabase()

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pocket Manager",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root {
    --bg:#0d0d0d; --surface:#161616; --surface2:#1f1f1f; --surface3:#282828;
    --gold:#f5c542; --gold2:#e8a900; --green:#22c55e; --red:#ef4444;
    --blue:#38bdf8; --orange:#fb923c; --purple:#a78bfa;
    --text:#f0f0f0; --muted:#6b6b6b; --border:#252525;
}
.stApp { background:var(--bg) !important; font-family:'DM Sans',sans-serif !important; color:var(--text) !important; }
.stApp > header { display:none !important; }
section[data-testid="stSidebar"] { background:var(--surface) !important; border-right:1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color:var(--text) !important; }
section[data-testid="stSidebar"] label { color:var(--muted) !important; font-size:0.72rem !important; text-transform:uppercase; letter-spacing:.12em; font-weight:700; }
.stButton > button { background:var(--gold) !important; color:#000 !important; border:none !important; border-radius:8px !important; font-family:'DM Sans',sans-serif !important; font-weight:700 !important; transition:all .15s ease !important; }
.stButton > button:hover { background:var(--gold2) !important; transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(245,197,66,.3) !important; }
.stTextInput input, .stNumberInput input { background:var(--surface2) !important; border:1px solid var(--border) !important; border-radius:8px !important; color:var(--text) !important; }
.stSelectbox [data-baseweb="select"] > div { background:var(--surface2) !important; border-color:var(--border) !important; color:var(--text) !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--surface) !important; border-radius:10px; padding:4px; gap:4px; }
.stTabs [data-baseweb="tab"] { background:transparent !important; border:none !important; border-radius:7px !important; color:var(--muted) !important; font-family:'DM Sans',sans-serif !important; font-weight:600 !important; font-size:.85rem !important; }
.stTabs [aria-selected="true"] { background:var(--gold) !important; color:#000 !important; }
div[data-testid="metric-container"] { background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:12px !important; padding:1rem !important; }
h1 { font-family:'Bebas Neue',sans-serif !important; letter-spacing:.05em !important; font-size:2.8rem !important; color:var(--gold) !important; margin-bottom:0 !important; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.25rem 1.5rem; margin-bottom:.75rem; }
.card-gold { border-left:3px solid var(--gold); }
.card-green { border-left:3px solid var(--green); }
.card-red { border-left:3px solid var(--red); }
.card-blue { border-left:3px solid var(--blue); }
.tag { display:inline-block; padding:2px 10px; border-radius:99px; font-size:.72rem; font-weight:700; }
.tag-food { background:rgba(251,146,60,.15); color:#fb923c; }
.tag-outing { background:rgba(56,189,248,.15); color:#38bdf8; }
.tag-shopping { background:rgba(167,139,250,.15); color:#a78bfa; }
.tag-recharge { background:rgba(34,197,94,.15); color:#22c55e; }
.tag-other { background:rgba(107,107,107,.15); color:#9ca3af; }
.tag-income { background:rgba(245,197,66,.15); color:#f5c542; }
.tag-pocket { background:rgba(34,197,94,.2); color:#22c55e; }
.tx-row { display:flex; align-items:center; justify-content:space-between; padding:.65rem 1rem; border-radius:10px; background:var(--surface2); margin-bottom:.4rem; border:1px solid var(--border); }
.tx-row:hover { border-color:var(--gold); }
.tx-exp { color:var(--red); font-weight:700; }
.tx-inc { color:var(--green); font-weight:700; }
.alert { padding:.75rem 1rem; border-radius:10px; font-weight:600; font-size:.9rem; margin-bottom:.5rem; }
.alert-danger { background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.3); color:#ef4444; }
.alert-warn { background:rgba(245,197,66,.1); border:1px solid rgba(245,197,66,.3); color:#f5c542; }
.alert-good { background:rgba(34,197,94,.1); border:1px solid rgba(34,197,94,.3); color:#22c55e; }
.alert-info { background:rgba(56,189,248,.1); border:1px solid rgba(56,189,248,.3); color:#38bdf8; }
.login-wrap { max-width:380px; margin:3rem auto; background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:2.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
CATEGORIES = {
    "🍔 Food / Canteen": "food",
    "🎉 Friends Outing": "outing",
    "👕 Shopping / Clothes": "shopping",
    "📱 Recharge / Internet": "recharge",
    "📦 Other": "other",
}
CAT_COLORS = {"food":"#fb923c","outing":"#38bdf8","shopping":"#a78bfa","recharge":"#22c55e","other":"#6b7280"}

# ─── DB Helpers ────────────────────────────────────────────────────────────────
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def get_user(username):
    r = sb.table("users").select("*").eq("username", username.lower().strip()).execute()
    return r.data[0] if r.data else None

def register_user(username, pin, pm, due_day, goal):
    try:
        sb.table("users").insert({
            "username": username.lower().strip(),
            "pin_hash": hash_pin(pin),
            "pocket_money_expected": float(pm),
            "pocket_money_due_day": int(due_day),
            "savings_goal": float(goal),
        }).execute()
        return True, "ok"
    except Exception as e:
        return False, str(e)

def get_transactions(user_id, year=None, month=None):
    q = sb.table("transactions").select("*").eq("user_id", user_id).order("date", desc=True)
    if year and month:
        start = f"{year}-{str(month).zfill(2)}-01"
        end = f"{year}-{str(month).zfill(2)}-{calendar.monthrange(year,month)[1]}"
        q = q.gte("date", start).lte("date", end)
    return q.execute().data or []

def add_transaction(user_id, tx_type, amount, category, note, tx_date):
    sb.table("transactions").insert({
        "user_id": user_id, "type": tx_type, "amount": float(amount),
        "category": category, "note": note, "date": str(tx_date),
    }).execute()

def get_budgets(user_id, year, month):
    r = sb.table("budgets").select("*").eq("user_id", user_id).eq("year", year).eq("month", month).execute()
    result = {"food":1000,"outing":700,"shopping":500,"recharge":300,"other":300}
    for row in (r.data or []):
        result[row["category"]] = row["amount"]
    return result

def set_budget(user_id, category, amount, year, month):
    ex = sb.table("budgets").select("id").eq("user_id",user_id).eq("category",category).eq("year",year).eq("month",month).execute()
    if ex.data:
        sb.table("budgets").update({"amount":float(amount)}).eq("id",ex.data[0]["id"]).execute()
    else:
        sb.table("budgets").insert({"user_id":user_id,"category":category,"amount":float(amount),"year":year,"month":month}).execute()

def update_user(user_id, pm, due_day, goal):
    sb.table("users").update({"pocket_money_expected":float(pm),"pocket_money_due_day":int(due_day),"savings_goal":float(goal)}).eq("id",user_id).execute()

def pm_received_month(user_id, year, month):
    start = f"{year}-{str(month).zfill(2)}-01"
    end = f"{year}-{str(month).zfill(2)}-{calendar.monthrange(year,month)[1]}"
    r = sb.table("transactions").select("amount").eq("user_id",user_id).eq("type","pocket_money").gte("date",start).lte("date",end).execute()
    return sum(x["amount"] for x in (r.data or []))

def month_totals(txns):
    spent = sum(t["amount"] for t in txns if t["type"]=="expense")
    earned = sum(t["amount"] for t in txns if t["type"] in ("income","pocket_money"))
    return spent, earned

# ══════════════════════════════════════════════════════════
# LOGIN / REGISTER SCREEN
# ══════════════════════════════════════════════════════════
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("# 💸 POCKET MANAGER")
    st.markdown("<p style='color:#6b6b6b;margin-bottom:1.5rem;font-size:.9rem'>Track your money. Build the habit.</p>", unsafe_allow_html=True)

    mode = st.radio("", ["🔐 Login", "✨ Sign Up"], horizontal=True, label_visibility="collapsed")
    st.markdown("")

    if "Login" in mode:
        uname = st.text_input("Username")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        if st.button("Login →", use_container_width=True):
            if not uname.strip():
                st.error("Enter your username!")
            elif len(pin) != 4 or not pin.isdigit():
                st.error("PIN must be exactly 4 digits!")
            else:
                u = get_user(uname)
                if u and u["pin_hash"] == hash_pin(pin):
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Wrong username or PIN!")
    else:
        uname = st.text_input("Choose a Username")
        col1, col2 = st.columns(2)
        with col1: pin = st.text_input("Choose PIN", type="password", max_chars=4)
        with col2: pin2 = st.text_input("Confirm PIN", type="password", max_chars=4)
        pm = st.number_input("Monthly Pocket Money Expected (₹)", value=3500, step=100, min_value=0)
        due = st.number_input("Papa usually gives money on which date?", value=1, min_value=1, max_value=28,
                               help="e.g. if he gives on 1st of every month, enter 1")
        goal = st.number_input("Monthly Savings Goal (₹)", value=500, step=50, min_value=0)
        if st.button("Create Account →", use_container_width=True):
            if not uname.strip(): st.error("Enter a username!")
            elif len(pin) != 4 or not pin.isdigit(): st.error("PIN must be 4 digits!")
            elif pin != pin2: st.error("PINs don't match!")
            elif get_user(uname): st.error("Username already taken!")
            else:
                ok, msg = register_user(uname, pin, pm, due, goal)
                if ok: st.success("Account created! Please login now ✅")
                else: st.error(f"Error: {msg}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
import plotly.graph_objects as go

# Refresh user
user = get_user(st.session_state.user["username"]) or st.session_state.user
st.session_state.user = user

now = date.today()
cur_year, cur_month = now.year, now.month
pm_exp = float(user["pocket_money_expected"])
due_day = int(user["pocket_money_due_day"])
goal = float(user["savings_goal"])

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 👋 {user['username'].title()}")
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    new_pm = st.number_input("Pocket Money (₹/mo)", value=pm_exp, step=100.0)
    new_due = st.number_input("Papa gives on day", value=due_day, min_value=1, max_value=28)
    new_goal = st.number_input("Savings Goal (₹/mo)", value=goal, step=50.0)
    if st.button("Save Settings", use_container_width=True):
        update_user(user["id"], new_pm, new_due, new_goal)
        st.success("Saved! ✅"); st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Monthly Budgets")
    budgets = get_budgets(user["id"], cur_year, cur_month)
    new_buds = {}
    for label, key in list(CATEGORIES.items())[:4]:
        new_buds[key] = st.number_input(label, value=float(budgets.get(key,300)), step=50.0, key=f"b_{key}")
    new_buds["other"] = budgets.get("other", 300)
    if st.button("Update Budgets", use_container_width=True):
        for k,v in new_buds.items():
            set_budget(user["id"], k, v, cur_year, cur_month)
        st.success("Updated! ✅"); st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None; st.rerun()

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 💸 POCKET MANAGER")
st.markdown(f"<div style='color:#6b6b6b;font-size:.85rem;margin-bottom:.75rem'>{now.strftime('%A, %d %B %Y')}</div>", unsafe_allow_html=True)

# ─── Pocket Money Alert (THE KEY FEATURE) ─────────────────────────────────────
pm_got = pm_received_month(user["id"], cur_year, cur_month)
due_date = date(cur_year, cur_month, due_day)
days_late = (now - due_date).days

if pm_got == 0:
    if now.day > due_day:
        st.markdown(f"""<div class='alert alert-danger'>
            🚨 <b>Pocket money not received!</b> Was due on <b>{due_date.strftime('%d %B')}</b> — 
            <b>{days_late} day{'s' if days_late!=1 else ''} late</b>. Time to ask Papa! 😤
        </div>""", unsafe_allow_html=True)
    elif now.day == due_day:
        st.markdown(f"<div class='alert alert-warn'>📅 <b>Pocket money due today!</b> Expected ₹{pm_exp:,.0f} — log it when you receive it!</div>", unsafe_allow_html=True)
    else:
        days_to = (due_date - now).days
        st.markdown(f"<div class='alert alert-info'>📅 Pocket money due in <b>{days_to} days</b> ({due_date.strftime('%d %b')}). Expected: ₹{pm_exp:,.0f}</div>", unsafe_allow_html=True)
elif pm_got < pm_exp:
    short = pm_exp - pm_got
    st.markdown(f"<div class='alert alert-warn'>⚠️ Got ₹{pm_got:,.0f} but expected ₹{pm_exp:,.0f}. Still <b>₹{short:,.0f} short</b> — remind Papa!</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='alert alert-good'>✅ Full pocket money received this month — ₹{pm_got:,.0f}. Let's manage it well!</div>", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "➕ Add Transaction", "📊 Monthly Report", "💰 Savings"])

# ══════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════
with tab1:
    txns = get_transactions(user["id"], cur_year, cur_month)
    budgets = get_budgets(user["id"], cur_year, cur_month)
    spent, earned = month_totals(txns)
    eff_budget = max(pm_got, 0) + sum(t["amount"] for t in txns if t["type"]=="income")
    if eff_budget == 0: eff_budget = pm_exp
    remaining = eff_budget - spent
    num_days = calendar.monthrange(cur_year, cur_month)[1]
    days_left = (date(cur_year, cur_month, num_days) - now).days
    spend_pct = int(spent/eff_budget*100) if eff_budget > 0 else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("💼 Available", f"₹{eff_budget:,.0f}")
    with c2: st.metric("💸 Spent", f"₹{spent:,.0f}", delta=f"-{spend_pct}%", delta_color="inverse")
    with c3: st.metric("🤑 Remaining", f"₹{remaining:,.0f}")
    with c4: st.metric("📅 Days Left", f"{days_left}")

    bar_c = "#ef4444" if spend_pct>=90 else "#f5c542" if spend_pct>=70 else "#22c55e"
    if spend_pct>=100: tip,tcls="🚨 Budget finished! Stop spending now!","alert-danger"
    elif spend_pct>=80: tip,tcls="⚠️ 80% used — be careful!","alert-warn"
    elif spend_pct>=60: tip,tcls="👀 Past halfway — slow down a bit","alert-warn"
    else: tip,tcls="✅ On track — keep it up!","alert-good"

    st.markdown(f'<div class="alert {tcls}" style="margin-top:.5rem">{tip}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;font-size:.8rem;color:#6b6b6b;margin-bottom:4px'>
        <span>₹0</span><span>₹{spent:,.0f} / ₹{eff_budget:,.0f}</span>
    </div>
    <div style='background:#1f1f1f;border-radius:99px;height:14px;overflow:hidden;border:1px solid #252525'>
        <div style='background:{bar_c};height:100%;width:{min(spend_pct,100)}%;border-radius:99px;box-shadow:0 0 10px {bar_c}66'></div>
    </div>
    <div style='text-align:right;font-size:.75rem;color:#6b6b6b;margin-bottom:1rem'>{spend_pct}% used</div>
    """, unsafe_allow_html=True)

    if days_left > 0 and remaining > 0:
        per_day = remaining / days_left
        st.markdown(f"""
        <div class='card card-gold'>
            <div style='font-size:.72rem;color:#6b6b6b;text-transform:uppercase;letter-spacing:.1em'>Safe to spend per day</div>
            <div style='font-size:2.5rem;font-family:"Bebas Neue";color:#f5c542'>₹{per_day:.0f} <span style='font-size:1rem;color:#6b6b6b'>/ day</span></div>
            <div style='font-size:.8rem;color:#6b6b6b'>Stay under this to hit your savings goal 🙏</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Category Budgets")
    cat_spent = {k:0 for k in CATEGORIES.values()}
    for t in txns:
        if t["type"]=="expense" and t.get("category") in cat_spent:
            cat_spent[t["category"]] += t["amount"]

    cols = st.columns(2)
    for i,(label,key) in enumerate(CATEGORIES.items()):
        bud = budgets.get(key,0)
        used = cat_spent.get(key,0)
        pct = int(used/bud*100) if bud>0 else 0
        bc = "#ef4444" if pct>=90 else "#f5c542" if pct>=70 else CAT_COLORS.get(key,"#6b6b6b")
        with cols[i%2]:
            st.markdown(f"""
            <div class='card' style='padding:.9rem 1.1rem;margin-bottom:.5rem'>
                <div style='display:flex;justify-content:space-between'>
                    <span style='font-size:.9rem;font-weight:600'>{label}</span>
                    <span style='font-size:.8rem;color:#6b6b6b'>₹{used:,.0f} / ₹{bud:,.0f}</span>
                </div>
                <div style='background:#1f1f1f;border-radius:99px;height:6px;overflow:hidden;margin:8px 0 0'>
                    <div style='background:{bc};height:100%;width:{min(pct,100)}%;border-radius:99px'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### Recent Transactions")
    if not txns:
        st.markdown("<div class='card' style='text-align:center;padding:2rem;color:#6b6b6b'>No transactions yet — add one!</div>", unsafe_allow_html=True)
    else:
        for t in txns[:8]:
            is_inc = t["type"] in ("income","pocket_money")
            sign = "+" if is_inc else "−"
            amt_cls = "tx-inc" if is_inc else "tx-exp"
            if t["type"]=="pocket_money": tag_text,tag_cls="POCKET MONEY","tag-pocket"
            elif t["type"]=="income": tag_text,tag_cls="INCOME","tag-income"
            else: tag_text,tag_cls=t.get("category","other").upper(),f"tag-{t.get('category','other')}"
            st.markdown(f"""
            <div class='tx-row'>
                <div>
                    <div style='font-weight:600;font-size:.95rem'>{t.get("note","") or "—"}</div>
                    <div style='display:flex;gap:6px;margin-top:3px'>
                        <span class='tag {tag_cls}'>{tag_text}</span>
                        <span style='font-size:.72rem;color:#6b6b6b'>{t["date"]}</span>
                    </div>
                </div>
                <span class='{amt_cls}'>{sign}₹{t["amount"]:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — ADD TRANSACTION
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Log a Transaction")
    tx_label = st.radio("", ["💸 Expense","💰 Extra Income","🏠 Pocket Money Received"], horizontal=True, label_visibility="collapsed")

    col_a,col_b = st.columns(2)
    with col_a: tx_amt = st.number_input("Amount (₹)", min_value=1, max_value=100000, value=50)
    with col_b: tx_date = st.date_input("Date", value=date.today())

    tx_note = ""; tx_cat = "other"; tx_type = "expense"

    if "Expense" in tx_label:
        cat_lbl = st.selectbox("Category", list(CATEGORIES.keys()))
        tx_cat = CATEGORIES[cat_lbl]; tx_type = "expense"
        tx_note = st.text_input("Note (optional)", placeholder="e.g. Lunch at canteen")
    elif "Extra Income" in tx_label:
        tx_type = "income"; tx_cat = "income"
        tx_note = st.text_input("Source", placeholder="e.g. Freelance, birthday gift...")
    else:
        tx_type = "pocket_money"; tx_cat = "pocket_money"
        already = pm_received_month(user["id"], cur_year, cur_month)
        if already > 0:
            st.markdown(f"<div class='alert alert-info'>Already logged ₹{already:,.0f} as pocket money this month.</div>", unsafe_allow_html=True)
        tx_note = "Pocket money from Papa"

    if st.button("✅ Add Transaction", use_container_width=True):
        add_transaction(user["id"], tx_type, tx_amt, tx_cat, tx_note, tx_date)
        msgs = {"expense":f"Expense ₹{tx_amt:,} logged!","income":f"Income ₹{tx_amt:,} logged!","pocket_money":f"Pocket money ₹{tx_amt:,} logged!"}
        st.success(msgs[tx_type]+" 🎉"); st.rerun()

    st.markdown("---")
    st.markdown("#### 🗑️ Delete a Transaction")
    all_txns = get_transactions(user["id"])
    if all_txns:
        opts = {f"[{t['date']}] {'−' if t['type']=='expense' else '+'} ₹{t['amount']:,.0f} — {(t.get('note','') or t.get('category',''))[:30]}": t["id"] for t in all_txns[:20]}
        sel = st.selectbox("Select to delete", ["— choose —"] + list(opts.keys()))
        if st.button("Delete ❌", use_container_width=True):
            if sel != "— choose —":
                sb.table("transactions").delete().eq("id", opts[sel]).execute()
                st.success("Deleted!"); st.rerun()
    else:
        st.caption("No transactions yet.")

# ══════════════════════════════════════════════════════════
# TAB 3 — MONTHLY REPORT
# ══════════════════════════════════════════════════════════
with tab3:
    col_m,col_y = st.columns(2)
    with col_m: sel_month = st.selectbox("Month", range(1,13), index=cur_month-1, format_func=lambda x: calendar.month_name[x])
    with col_y: sel_year = st.selectbox("Year", [cur_year-1, cur_year], index=1)

    m_txns = get_transactions(user["id"], sel_year, sel_month)
    m_spent, m_earned = month_totals(m_txns)
    m_pm = sum(t["amount"] for t in m_txns if t["type"]=="pocket_money")
    m_extra = sum(t["amount"] for t in m_txns if t["type"]=="income")
    m_budget = (m_pm + m_extra) if (m_pm+m_extra)>0 else pm_exp
    m_saved = m_budget - m_spent

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("💸 Total Spent", f"₹{m_spent:,.0f}")
    with c2: st.metric("🏠 Pocket Money", f"₹{m_pm:,.0f}")
    with c3: st.metric("💰 Extra Income", f"₹{m_extra:,.0f}")
    with c4: st.metric("🤑 Saved", f"₹{m_saved:,.0f}")

    # Daily bar chart
    nd = calendar.monthrange(sel_year, sel_month)[1]
    days = list(range(1, nd+1))
    d_exp = {}; d_inc = {}
    for t in m_txns:
        d = int(t["date"].split("-")[2])
        if t["type"]=="expense": d_exp[d] = d_exp.get(d,0)+t["amount"]
        elif t["type"] in ("income","pocket_money"): d_inc[d] = d_inc.get(d,0)+t["amount"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=days, y=[d_exp.get(d,0) for d in days], name="Spent", marker_color="#ef4444", opacity=.85, width=.6))
    fig.add_trace(go.Bar(x=days, y=[d_inc.get(d,0) for d in days], name="Received", marker_color="#22c55e", opacity=.85, width=.6))
    fig.add_hline(y=pm_exp/nd, line_dash="dot", line_color="#f5c542", line_width=1.5, opacity=.7)
    fig.add_annotation(x=days[-1], y=pm_exp/nd+20, text="Daily limit", showarrow=False,
                       font=dict(color="#f5c542",size=10,family="DM Sans"), xanchor="right")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', barmode='group',
        title=dict(text=f"{calendar.month_name[sel_month]} {sel_year} — Daily Breakdown",
                   font=dict(family='Bebas Neue',size=20,color='#f0f0f0'), x=0),
        xaxis=dict(tickfont=dict(color='#6b6b6b',family='DM Sans',size=10), showgrid=False, tickmode='linear', dtick=1),
        yaxis=dict(tickfont=dict(color='#6b6b6b'), gridcolor='rgba(37,37,37,.8)', tickprefix="₹"),
        legend=dict(font=dict(color='#f0f0f0',family='DM Sans'), bgcolor='rgba(0,0,0,0)', x=0, y=1.1, orientation='h'),
        hoverlabel=dict(bgcolor='#161616',font_color='#f0f0f0',font_family='DM Sans'),
        margin=dict(l=10,r=10,t=50,b=10), height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

    col_pie, col_tips = st.columns(2)
    with col_pie:
        cat_totals = {}
        for t in m_txns:
            if t["type"]=="expense":
                c = t.get("category","other")
                cat_totals[c] = cat_totals.get(c,0)+t["amount"]
        if cat_totals:
            dlabels = [next((l for l,v in CATEGORIES.items() if v==k),k) for k in cat_totals]
            fig2 = go.Figure(go.Pie(
                labels=dlabels, values=list(cat_totals.values()), hole=.55,
                marker=dict(colors=[CAT_COLORS.get(k,"#6b6b6b") for k in cat_totals],line=dict(color='#0d0d0d',width=3)),
                textfont=dict(family='DM Sans',size=11,color='white'),
                hovertemplate="<b>%{label}</b><br>₹%{value:,}<br>%{percent}<extra></extra>",
            ))
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True, legend=dict(font=dict(color='#f0f0f0',family='DM Sans',size=10),bgcolor='rgba(0,0,0,0)'),
                annotations=[dict(text=f"₹{m_spent:,.0f}",x=.5,y=.5,font=dict(size=18,color='#f0f0f0',family='Bebas Neue'),showarrow=False)],
                margin=dict(l=0,r=0,t=30,b=10), height=280,
                title=dict(text="Where Did It Go?",font=dict(family='Bebas Neue',size=18,color='#f0f0f0'),x=0),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown("<div class='card' style='text-align:center;padding:2rem;color:#6b6b6b'>No expense data</div>", unsafe_allow_html=True)

    with col_tips:
        st.markdown("#### 💡 Tips")
        if cat_totals:
            big = max(cat_totals, key=cat_totals.get)
            tip_map = {
                "food":f"🍔 ₹{cat_totals.get('food',0):,.0f} on food! Try home meals to save ₹200+/week.",
                "outing":f"🎉 ₹{cat_totals.get('outing',0):,.0f} on outings! Go Dutch next time.",
                "shopping":f"👕 ₹{cat_totals.get('shopping',0):,.0f} on shopping! Need or want?",
                "recharge":f"📱 ₹{cat_totals.get('recharge',0):,.0f} on recharge! Check cheaper plans.",
                "other":f"📦 ₹{cat_totals.get('other',0):,.0f} in 'other' — track these better!",
            }
            st.markdown(f"<div class='card card-gold'><b>Biggest spend:</b><br>{tip_map.get(big,'')}</div>", unsafe_allow_html=True)

        if m_saved >= goal:
            st.markdown(f"<div class='card card-green'>🎉 Savings goal achieved! ₹{m_saved:,.0f} saved!</div>", unsafe_allow_html=True)
        elif m_saved > 0:
            st.markdown(f"<div class='card card-gold'>💪 ₹{goal-m_saved:,.0f} more to hit your goal!</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card card-red'>🚨 Overspent by ₹{abs(m_saved):,.0f}. Be careful next time!</div>", unsafe_allow_html=True)

        if sel_month==cur_month and sel_year==cur_year and now.day>1:
            proj = (m_spent/now.day)*nd
            st.markdown(f"""
            <div class='card card-blue'>
                <div style='font-size:.72rem;color:#6b6b6b;text-transform:uppercase'>Projected Month Total</div>
                <div style='font-size:1.8rem;font-family:"Bebas Neue";color:#38bdf8'>₹{proj:,.0f}</div>
                <div style='font-size:.8rem;color:#6b6b6b'>At current spending rate</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 4 — SAVINGS
# ══════════════════════════════════════════════════════════
with tab4:
    cur_txns = get_transactions(user["id"], cur_year, cur_month)
    c_spent, c_earned = month_totals(cur_txns)
    c_budget = max(pm_got,0) + sum(t["amount"] for t in cur_txns if t["type"]=="income")
    if c_budget == 0: c_budget = pm_exp
    c_saved = c_budget - c_spent
    g_pct = min(int(c_saved/goal*100),100) if goal>0 else 0
    bar_c = "#22c55e" if g_pct>=100 else "#f5c542" if g_pct>=50 else "#ef4444"
    status = "🎉 Goal Complete!" if g_pct>=100 else f"{g_pct}% of goal"

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("🎯 Monthly Goal", f"₹{goal:,.0f}")
    with c2: st.metric("💰 Saved This Month", f"₹{c_saved:,.0f}")
    with c3: st.metric("📊 Progress", f"{g_pct}%")

    st.markdown(f"""
    <div class='card' style='text-align:center;padding:2rem'>
        <div style='font-size:3.5rem;font-family:"Bebas Neue";color:{bar_c}'>{status}</div>
        <div style='background:#1f1f1f;border-radius:99px;height:16px;overflow:hidden;margin:1rem 0;border:1px solid #252525'>
            <div style='background:linear-gradient(90deg,{bar_c},{bar_c}88);height:100%;width:{g_pct}%;border-radius:99px;box-shadow:0 0 15px {bar_c}55'></div>
        </div>
        <div style='color:#6b6b6b;font-size:.85rem'>₹{c_saved:,.0f} saved of ₹{goal:,.0f} goal this month</div>
    </div>
    """, unsafe_allow_html=True)

    # Month-by-month chart
    monthly = []
    for m in range(1, cur_month+1):
        mt = get_transactions(user["id"], cur_year, m)
        ms, me = month_totals(mt)
        mb = me if me>0 else pm_exp
        monthly.append({"m": calendar.month_abbr[m], "s": mb-ms})

    if len(monthly)>1:
        st.markdown("#### Month-wise Savings This Year")
        fig3 = go.Figure(go.Bar(
            x=[x["m"] for x in monthly], y=[x["s"] for x in monthly],
            marker_color=["#22c55e" if x["s"]>=goal else "#ef4444" if x["s"]<0 else "#f5c542" for x in monthly],
            text=[f"₹{x['s']:,.0f}" for x in monthly], textposition='outside',
            textfont=dict(family='DM Sans',color='#f0f0f0',size=11),
        ))
        fig3.add_hline(y=goal, line_dash="dash", line_color="#f5c542", line_width=2)
        fig3.add_annotation(x=monthly[-1]["m"], y=goal+50, text=f"Goal ₹{goal:,.0f}",
                            showarrow=False, font=dict(color="#f5c542",size=10,family="DM Sans"), xanchor="right")
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#6b6b6b',family='DM Sans'), showgrid=False),
            yaxis=dict(tickfont=dict(color='#6b6b6b'), gridcolor='rgba(37,37,37,.6)', tickprefix="₹"),
            margin=dict(l=10,r=10,t=20,b=10), height=280,
            hoverlabel=dict(bgcolor='#161616',font_family='DM Sans'),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### 🧠 Money Saving Tips")
    tips = [
        ("🍱","Bring tiffin from home","Save ₹200-300/week vs canteen"),
        ("🤝","Go Dutch with friends","Split bills — always"),
        ("📋","Make a shopping list first","Stop impulse buying"),
        ("💵","Use cash, not UPI","Physical money = more careful"),
        ("🎯","50-30-20 rule","50% needs, 30% wants, 20% savings"),
        ("📅","Log every expense daily","Awareness = less overspending"),
    ]
    cols_t = st.columns(2)
    for i,(emoji,title,desc) in enumerate(tips):
        with cols_t[i%2]:
            st.markdown(f"""
            <div class='card' style='padding:.9rem 1.1rem;margin-bottom:.5rem'>
                <div style='font-size:1.4rem'>{emoji}</div>
                <div style='font-weight:700;font-size:.9rem;margin-top:4px'>{title}</div>
                <div style='color:#6b6b6b;font-size:.78rem;margin-top:2px'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
