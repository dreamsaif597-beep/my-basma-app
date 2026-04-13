import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# حفظ بيانات الموظفين وإعدادات المدير في الـ session_state لضمان عدم الضياع أثناء التبديل
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
    try: requests.post(FORM_URL, data=payload, timeout=7)
    except: st.error("فشل في الاتصال بالسيرفر")

@st.cache_data(ttl=2)
def fetch_and_clean_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        for col in ['name', 'type', 'data', 'time']:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        resets = df[df['type'] == "تصفية أسبوعية"].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:].reset_index(drop=True)
        return df
    except: return pd.DataFrame()

# --- واجهة المستخدم الحديثة (Modern UI) ---
st.set_page_config(page_title="Basma Smart System", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #050505 0%, #1a1a2e 100%);
        color: white;
    }}
    .main-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        color: black; font-weight: bold; border: none; border-radius: 10px;
    }}
    div[data-testid="stMetricValue"] {{ color: #00f2fe !important; }}
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- تسجيل الدخول ---
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>✨ نظام بصمة البسمة</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        role = st.radio("تسجيل كـ:", ["موظف", "المدير"], horizontal=True)
        if role == "موظف":
            u_name = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
            u_pass = st.text_input("رمز المرور:", type="password")
            if st.button("دخول"):
                if u_pass == STAFF_DATA[u_name]["pass"]:
                    st.session_state.update({'auth':True, 'user':u_name, 'role':"موظف"})
                    st.rerun()
                else: st.error("❌ الرمز غير صحيح")
        else:
            a_pass = st.text_input("رمز المدير:", type="password")
            if st.button("دخول المدير"):
                if a_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("❌ الرمز غير صحيح")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- شريط جانبي (Sidebar) ---
with st.sidebar:
    st.write(f"👤 المستخدم: **{st.session_state.get('user', 'المدير')}**")
    if st.button("🚪 خروج"):
        st.session_state.update({'auth': False})
        st.rerun()
    if st.button("🔄 تحديث"):
        st.cache_data.clear()
        st.rerun()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp = STAFF_DATA[name]
    st.title(f"👋 أهلاً {name}")
    
    df = fetch_and_clean_data()
    user_rec = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    # الحسابات
    sal = emp['salary']
    disc_total = int(user_rec['discount'].sum())
    bonus_total = int(user_rec[user_rec['type'] == "مكافأة"]['overtime'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب", f"{sal:,}")
    c2.metric("الخصومات", f"{disc_total:,}")
    c3.metric("الصافي", f"{sal - disc_total + bonus_total:,}")

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    # منطق الشفتات
    target_time_str = ""
    if emp['type'] == 'double':
        shift = st.radio("اختر الوجبة الحالية:", ["الوجبة الأولى", "الوجبة الثانية"], horizontal=True)
        target_time_str = emp['s1'] if shift == "الوجبة الأولى" else emp['s2']
        type_prefix = f"حضور ({shift})"
    else:
        target_time_str = emp['start']
        type_prefix = "حضور"

    col_h, col_i = st.columns(2)
    if col_h.button("📥 بصمة حضور"):
        t_start = datetime.strptime(target_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        delay = (now - t_start).total_seconds() / 60
        # استخدام معادلة المدير للخصم
        penalty = int(delay * st.session_state['penalty_rate']) if delay > 5 else 0
        send_to_google(name, c_date, c_time, type_prefix, penalty, 0)
        st.success(f"✅ تم الحضور. الخصم: {penalty:,}")
        st.cache_data.clear(); time.sleep(1); st.rerun()

    if col_i.button("📤 بصمة انصراف"):
        send_to_google(name, c_date, c_time, "انصراف", 0, 0)
        st.info("✅ تم الانصراف")
        st.cache_data.clear(); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📊 كشف حركاتي"):
        st.table(user_rec[['data', 'time', 'type', 'discount']].rename(columns={'data':'التاريخ', 'time':'الوقت', 'type':'النوع', 'discount':'الخصم'}))

# --- واجهة المدير (كاملة الإضافات) ---
elif st.session_state['role'] == "المدير":
    st.title("👑 لوحة التحكم")
    
    # 1. التحكم بالمعادلة
    with st.expander("⚙️ التحكم بمعادلة الخصم"):
        new_rate = st.number_input("سعر دقيقة التأخير (دينار):", value=st.session_state['penalty_rate'], step=50)
        if st.button("تحديث المعادلة"):
            st.session_state['penalty_rate'] = new_rate
            st.success("تم الحفظ")

    # 2. إدارة الموظفين
    with st.expander("👤 إدارة بيانات الموظفين"):
        m_emp = st.selectbox("اختر موظف لتعديله:", list(STAFF_DATA.keys()))
        curr = STAFF_DATA[m_emp]
        new_sal = st.number_input("الراتب:", value=curr['salary'])
        new_p = st.text_input("الرمز:", value=curr['pass'])
        if curr['type'] == 'single':
            t_s = st.text_input("الحضور:", value=curr['start'])
            t_e = st.text_input("الانصراف:", value=curr['end'])
            if st.button("حفظ التعديل"):
                st.session_state['staff_registry'][m_emp].update({"salary":new_sal, "pass":new_p, "start":t_s, "end":t_e})
                st.success("تم التحديث")
        else:
            c1, c2, c3, c4 = st.columns(4)
            v1 = c1.text_input("س1", curr['s1'])
            v2 = c2.text_input("إ1", curr['e1'])
            v3 = c3.text_input("س2", curr['s2'])
            v4 = c4.text_input("إ2", curr['e2'])
            if st.button("حفظ تعديل الوجبات"):
                st.session_state['staff_registry'][m_emp].update({"salary":new_sal, "pass":new_p, "s1":v1, "e1":v2, "s2":v3, "e2":v4})
                st.success("تم التحديث")

    # 3. الرواتب والطلبات
    df_raw = fetch_and_clean_data()
    t1, t2 = st.tabs(["📊 الرواتب", "📩 الطلبات"])
    
    with t1:
        if not df_raw.empty:
            clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
            totals = clean.groupby('name')[['discount', 'overtime']].sum()
            res = []
            for n, info in STAFF_DATA.items():
                d = int(totals.loc[n, 'discount']) if n in totals.index else 0
                o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
                res.append({"الاسم": n, "الراتب": info['salary'], "الخصم": d, "المكافأة": o, "الصافي": info['salary'] - d + o})
            st.table(pd.DataFrame(res))
            
            # مكافأة وغياب سريع
            cm1, cm2 = st.columns(2)
            with cm1:
                e_sel = st.selectbox("موظف للمكافأة:", list(STAFF_DATA.keys()))
                amt_b = st.number_input("المبلغ:", step=1000)
                if st.button("أضف مكافأة"):
                    send_to_google(e_sel, "مكافأة", "---", "مكافأة", 0, amt_b)
                    st.rerun()
            with cm2:
                e_g = st.selectbox("موظف للغياب:", list(STAFF_DATA.keys()))
                amt_g = st.number_input("خصم الغياب:", value=15000)
                if st.button("أضف خصم"):
                    send_to_google(e_g, "غياب", "---", "غياب", amt_g, 0)
                    st.rerun()

    with t2:
        if not df_raw.empty:
            pending = df_raw[df_raw['type'].str.contains("طلب", na=False)]
            archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
            pending = pending[~pending['data'].isin(archived)]
            for i, row in pending.iterrows():
                st.info(f"📍 {row['name']}: {row['type']} - {row['data']}")
                if st.button("موافقة والأرشفة", key=f"v{i}"):
                    if "سلفة" in row['type']:
                        send_to_google(row['name'], f"سلفة {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                    send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                    st.rerun()

    if st.button("♻️ تصفير الأسبوع"):
        send_to_google("النظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.balloons(); st.rerun()
