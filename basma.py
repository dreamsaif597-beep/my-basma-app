import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# ==========================================
# 1. الإعدادات والروابط (تأكد من صحتها)
# ==========================================
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# ==========================================
# 2. قاعدة بيانات الموظفين (Session State)
# ==========================================
if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
        "علي ماجد": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
    }

if 'penalty_rate' not in st.session_state:
    st.session_state['penalty_rate'] = 100

STAFF_DATA = st.session_state['staff_registry']

# ==========================================
# 3. الدوال البرمجية (Functions)
# ==========================================
def get_iraq_time():
    return datetime.utcnow() + timedelta(hours=3)

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,
        "entry.786801446": data_val,
        "entry.2093200411": time_val,
        "entry.1043553703": type_val,
        "entry.1254543219": int(discount),
        "entry.1151470082": int(overtime)
    }
    try:
        requests.post(FORM_URL, data=payload, timeout=7)
    except:
        st.error("⚠️ فشل في إرسال البيانات")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        for col in ['name', 'type', 'data', 'time']:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        
        # منطق التصفية الأسبوعية
        resets = df[df['type'] == "تصفية أسبوعية"].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:].reset_index(drop=True)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 4. التصميم واجهة المستخدم (Modern UI)
# ==========================================
st.set_page_config(page_title="Basma Smart System", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #050505 0%, #1a1a2e 100%); color: white; }
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
    }
    .stButton>button { 
        background: linear-gradient(45deg, #00f2fe, #4facfe); 
        color: black !important; font-weight: bold; border-radius: 10px; border: none; width: 100%;
    }
    div[data-testid="stMetricValue"] { color: #00f2fe !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# ==========================================
# 5. شاشة تسجيل الدخول
# ==========================================
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>✨ نظام بصمة البسمة</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        role = st.radio("نوع الدخول:", ["موظف", "الإدارة"], horizontal=True)
        if role == "موظف":
            u_name = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
            u_pass = st.text_input("رمز المرور:", type="password")
            if st.button("دخول"):
                if u_pass == STAFF_DATA[u_name]["pass"]:
                    st.session_state.update({'auth':True, 'user':u_name, 'role':"موظف"})
                    st.rerun()
                else: st.error("❌ الرمز خطأ")
        else:
            a_pass = st.text_input("رمز المدير:", type="password")
            if st.button("فتح الإدارة"):
                if a_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("❌ الرمز خطأ")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 6. واجهة الموظف
# ==========================================
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp = STAFF_DATA[name]
    st.markdown(f"## 👋 أهلاً {name}")
    
    df = fetch_data()
    # جلب سجلات الموظف الحالية (باستبعاد الطلبات والأرشفة من الجدول المالي)
    user_rec = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    col1, col2, col3 = st.columns(3)
    sal = emp['salary']
    disc = int(user_rec['discount'].sum())
    bon = int(user_rec[user_rec['type'] == "مكافأة"]['overtime'].sum())
    col1.metric("الراتب", f"{sal:,}")
    col2.metric("الخصم", f"{disc:,}")
    col3.metric("الصافي", f"{sal - disc + bon:,}")

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    if emp['type'] == 'double':
        shift = st.radio("الوجبة الحالية:", ["الوجبة الأولى", "الوجبة الثانية"], horizontal=True)
        target = emp['s1'] if shift == "الوجبة الأولى" else emp['s2']
        t_prefix = f"حضور ({shift})"
    else:
        target = emp['start']
        t_prefix = "حضور"

    ca, cb = st.columns(2)
    if ca.button("📥 بصمة حضور"):
        t_start = datetime.strptime(target, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        delay = (now - t_start).total_seconds() / 60
        penalty = int(delay * st.session_state['penalty_rate']) if delay > 5 else 0
        send_to_google(name, c_date, c_time, t_prefix, penalty, 0)
        st.success(f"تم الحضور. الخصم: {penalty:,}")
        st.cache_data.clear(); time.sleep(1); st.rerun()

    if cb.button("📤 بصمة انصراف"):
        send_to_google(name, c_date, c_time, "انصراف", 0, 0)
        st.info("تم الانصراف")
        st.cache_data.clear(); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📝 تقديم طلب سلفة/إجازة"):
        t_q = st.selectbox("النوع:", ["سلفة", "إجازة"])
        m_q = st.number_input("المبلغ (للسلفة):", step=5000)
        r_q = st.text_input("السبب:")
        if st.button("إرسال الطلب"):
            send_to_google(name, r_q, c_date, f"طلب {t_q}", m_q, 0)
            st.warning("تم الإرسال للمدير")

# ==========================================
# 7. واجهة المدير (كاملة وشاملة)
# ==========================================
elif st.session_state['role'] == "المدير":
    st.markdown("<h2 style='text-align: center;'>👑 لوحة التحكم الشاملة</h2>", unsafe_allow_html=True)
    df_raw = fetch_data()

    # --- أ. جدول الرواتب (هنا يتم عرضه) ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📊 كشف الرواتب الأسبوعي")
    if not df_raw.empty:
        # تصفية البيانات لحساب المبالغ فقط
        f_df = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = f_df.groupby('name')[['discount', 'overtime']].sum()
        
        payroll_list = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            payroll_list.append({
                "الموظف": n,
                "الراتب": f"{info['salary']:,}",
                "الخصم": f"{d:,}",
                "المكافأة": f"{o:,}",
                "الصافي": f"{(info['salary'] - d + o):,}"
            })
        st.table(pd.DataFrame(payroll_list))
    else:
        st.info("لا توجد بيانات دوام بعد")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ب. إدارة الطلبات ---
    st.subheader("📩 طلبات الموظفين")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived)]
        
        if pending.empty:
            st.write("✅ لا توجد طلبات جديدة")
        for i, row in pending.iterrows():
            with st.container():
                st.markdown(f'<div class="main-card"><b>{row["name"]}</b> يطلب {row["type"]} <br> التفاصيل: {row["data"]} | المبلغ: {row["discount"]:,}</div>', unsafe_allow_html=True)
                col_y, col_n = st.columns(2)
                if col_y.button("موافقة", key=f"y{i}"):
                    if "سلفة" in row['type']:
                        send_to_google(row['name'], f"سلفة {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                    send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                    st.cache_data.clear(); st.rerun()
                if col_n.button("رفض", key=f"n{i}"):
                    send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                    st.cache_data.clear(); st.rerun()

    # --- ج. إدارة الموظفين والإعدادات ---
    with st.expander("⚙️ تعديل بيانات الموظفين ومعادلة الخصم"):
        st.session_state['penalty_rate'] = st.number_input("سعر دقيقة التأخير:", value=st.session_state['penalty_rate'])
        
        target = st.selectbox("اختر موظف لتعديله:", list(STAFF_DATA.keys()))
        curr = STAFF_DATA[target]
        n_sal = st.number_input("الراتب:", value=curr['salary'])
        n_pass = st.text_input("الرمز:", value=curr['pass'])
        
        if curr['type'] == 'single':
            c1, c2 = st.columns(2)
            ts = c1.text_input("الحضور:", curr['start'])
            te = c2.text_input("الانصراف:", curr['end'])
            if st.button("حفظ التعديل"):
                st.session_state['staff_registry'][target].update({"salary":n_sal, "pass":n_pass, "start":ts, "end":te})
                st.success("تم التحديث")
        else:
            c1, c2, c3, c4 = st.columns(4)
            v1, v2, v3, v4 = c1.text_input("ح1", curr['s1']), c2.text_input("إ1", curr['e1']), c3.text_input("ح2", curr['s2']), c4.text_input("إ2", curr['e2'])
            if st.button("حفظ تعديل الشفتات"):
                st.session_state['staff_registry'][target].update({"salary":n_sal, "pass":n_pass, "s1":v1, "e1":v2, "s2":v3, "e2":v4})
                st.success("تم التحديث")

    # --- د. مكافأة وخصم يدوي ---
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("### ➕ مكافأة")
        eb = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="eb")
        ab = st.number_input("المبلغ:", step=1000, key="ab")
        if st.button("تأكيد المكافأة"):
            send_to_google(eb, "مكافأة إدارية", "---", "مكافأة", 0, ab)
            st.cache_data.clear(); st.rerun()
    with c_m2:
        st.markdown("### 🚫 خصم غياب")
        eg = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="eg")
        ag = st.number_input("المبلغ:", value=15000, key="ag")
        if st.button("تأكيد الخصم"):
            send_to_google(eg, "خصم يدوي", "---", "غياب", ag, 0)
            st.cache_data.clear(); st.rerun()

    st.divider()
    if st.button("♻️ تصفية الأسبوع (تصفير السجلات)"):
        send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.balloons(); st.cache_data.clear(); st.rerun()

# زر الخروج في الجانبي
if st.sidebar.button("🚪 خروج"):
    st.session_state['auth'] = False
    st.rerun()
