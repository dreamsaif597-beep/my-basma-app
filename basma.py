import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- التحكم بالدوام حسب الأيام (جديد) ---
WEEKLY_RULES = {
    "Saturday":  {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Sunday":    {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Monday":    {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Tuesday":   {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Wednesday": {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Thursday":  {"start": "16:00", "end": "23:00", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "Friday":    {"start": "14:00", "end": "21:00", "s1": "09:00", "e1": "13:00", "s2": "15:00", "e2": "21:00"},
}

if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "type": "single"},
        "علي ماجد": {"salary": 75000, "pass": "1177", "type": "single"},
    }

STAFF_DATA = st.session_state['staff_registry']

def get_iraq_time():
    return datetime.utcnow() + timedelta(hours=3)

# --- استايل الحداثة والواجهة الإلكترونية المتطورة ---
st.set_page_config(page_title="نظام بصمة البسمة الذكي", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button {
        border-radius: 12px; border: 1px solid #00d4ff; background-color: rgba(0, 212, 255, 0.05);
        color: #00d4ff; font-weight: bold; transition: 0.3s; width: 100%; height: 3.5em;
    }
    .stButton>button:hover { background-color: #00d4ff; color: #000; box-shadow: 0 0 15px #00d4ff; }
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'monospace'; }
    .css-1r6slb0 { border: 1px solid #1e2630; border-radius: 15px; padding: 20px; background: #161b22; }
    h1, h2, h3 { color: #00d4ff !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name, "entry.786801446": data_val,
        "entry.2093200411": time_val, "entry.1043553703": type_val,
        "entry.1254543219": int(discount), "entry.1151470082": int(overtime)
    }
    try: requests.post(FORM_URL, data=payload, timeout=7)
    except: st.error("⚠️ فشل في إرسال البيانات")

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

# --- الدخول ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h1>🌐 Digital Login</h1>", unsafe_allow_html=True)
    role = st.radio("اختر الصلاحية:", ["موظف", "المدير"], horizontal=True)
    if role == "موظف":
        user_sel = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
        user_pass = st.text_input("الرمز السري:", type="password")
        if st.button("دخول النظام"):
            if user_pass == STAFF_DATA[user_sel]["pass"]:
                st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
                st.rerun()
            else: st.error("❌ الرمز غير صحيح")
    else:
        admin_pass = st.text_input("رمز الإدارة:", type="password")
        if st.button("دخول الإدارة"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.update({'auth':True, 'role':"المدير"})
                st.rerun()
            else: st.error("❌ الرمز غير صحيح")
    st.stop()

st.sidebar.button("🚪 خروج", on_click=lambda: st.session_state.update({'auth': False}))
if st.sidebar.button("🔄 تحديث"):
    st.cache_data.clear()
    st.rerun()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    st.markdown(f"<h2>مرحباً، {name} 🛸</h2>", unsafe_allow_html=True)
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = STAFF_DATA[name]['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب الأساسي", f"{salary:,}")
    c2.metric("إجمالي الخصم", f"{total_disc:,}")
    c3.metric("الصافي المستحق", f"{salary - total_disc + manual_bonuses:,}")

    st.divider()
    now = get_iraq_time()
    day_name = now.strftime("%A")
    rules = WEEKLY_RULES.get(day_name)
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    # نظام اختيار الشفت للموظفين ذوي الشفتين
    shift_selected = "single"
    if STAFF_DATA[name]['type'] == 'double':
        shift_selected = st.radio("اختر الوجبة الحالية للبصمة:", ["الأولى", "الثانية"], horizontal=True)

    col_a, col_b = st.columns(2)
    
    if col_a.button("📥 تسجيل حضور"):
        # تحديد وقت البداية بناءً على اليوم والوجبة
        if STAFF_DATA[name]['type'] == 'single':
            t_ref = rules['start']
        else:
            t_ref = rules['s1'] if shift_selected == "الأولى" else rules['s2']
            
        t_start = datetime.strptime(t_ref, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        disc = int((now - t_start).total_seconds() / 60 * 100) if now > t_start + timedelta(minutes=5) else 0
        
        send_to_google(name, c_date, c_time, f"حضور ({shift_selected})", disc, 0)
        st.success(f"تم البصمة. الخصم: {disc:,}")
        time.sleep(1); st.cache_data.clear(); st.rerun()

    if col_b.button("📤 تسجيل انصراف"):
        if STAFF_DATA[name]['type'] == 'single':
            t_ref_e = rules['end']
        else:
            t_ref_e = rules['e1'] if shift_selected == "الأولى" else rules['e2']
            
        t_end = datetime.strptime(t_ref_e, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        ov = int((now - t_end).total_seconds() / 60 * 100) if now > t_end + timedelta(minutes=1) else 0
        
        send_to_google(name, c_date, c_time, f"انصراف ({shift_selected})", 0, ov)
        st.info("تم تسجيل الانصراف")
        time.sleep(1); st.cache_data.clear(); st.rerun()

    with st.expander("📊 سجل الحركات الذكي"):
        if not user_records.empty:
            view_df = user_records.copy()
            view_df['الوقت'] = view_df['data'] + " | " + view_df['time']
            view_df['المكافأة'] = view_df.apply(lambda x: x['overtime'] if x['type'] == "مكافأة" else 0, axis=1)
            st.table(view_df[['الوقت', 'type', 'discount', 'المكافأة']])

    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ", min_value=0, step=1000)
        reason = st.text_input("السبب")
        if st.button("إرسال الطلب"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("تم الإرسال للإدارة")

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h2>👑 Control Center</h2>", unsafe_allow_html=True)
    
    with st.expander("👤 إدارة وتعديل الموظفين"):
        mode = st.radio("العملية:", ["تعديل موظف", "إضافة جديد"], horizontal=True)
        if mode == "تعديل موظف":
            target = st.selectbox("الموظف:", list(STAFF_DATA.keys()))
            new_sal = st.number_input("الراتب الجديد:", value=STAFF_DATA[target]['salary'])
            if st.button("حفظ التغييرات"):
                st.session_state['staff_registry'][target]['salary'] = new_sal
                st.success("تم التحديث بنجاح")
        else:
            nn = st.text_input("الاسم:")
            nt = st.selectbox("النوع:", ["single", "double"])
            if st.button("إضافة للمنظومة"):
                st.session_state['staff_registry'][nn] = {"salary":75000, "pass":"1234", "type":nt}
                st.success("تمت الإضافة")

    st.divider()
    df_raw = fetch_and_clean_data()
    
    st.subheader("📩 البريد والطلبات")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived)]
        for i, row in pending[::-1].iterrows():
            st.info(f"طلب من {row['name']}: {row['type']} - {row['data']} ({row['discount']:,})")
            if st.button(f"موافقة {i}"):
                if "سلفة" in row['type']:
                    send_to_google(row['name'], f"سلفة: {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                st.rerun()

    st.divider()
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.subheader("➕ مكافأة")
        e_m = st.selectbox("للموظف:", list(STAFF_DATA.keys()), key="m1")
        a_m = st.number_input("المبلغ:", step=1000, key="am1")
        if st.button("منح مكافأة"):
            send_to_google(e_m, "مكافأة يدوية", "---", "مكافأة", 0, a_m)
            st.success("تم")
    with c_m2:
        st.subheader("🚫 غياب")
        e_g = st.selectbox("للموظف:", list(STAFF_DATA.keys()), key="g1")
        a_g = st.number_input("المبلغ:", value=15000, step=1000, key="ag1")
        if st.button("تسجيل غياب"):
            send_to_google(e_g, "غياب يدوي", "---", "غياب", a_g, 0)
            st.error("تم الخصم")

    st.divider()
    if st.button("📊 تقرير الرواتب النهائي"):
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الراتب": info['salary'], "الخصوم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))

    if st.button("🔄 تصفير البيانات الأسبوعية"):
        send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.balloons(); st.rerun()
