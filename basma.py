import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- سجل الموظفين مع أوقاتهم الثابتة ---
if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
        "علي ماجد": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
    }

if 'late_rate' not in st.session_state:
    st.session_state['late_rate'] = 100

STAFF_DATA = st.session_state['staff_registry']
LATE_RATE = st.session_state['late_rate']

def get_iraq_time():
    return datetime.utcnow() + timedelta(hours=3)

# --- استايل الواجهة ---
st.set_page_config(page_title="نظام بصمة البسمة الذكي", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { border-radius: 12px; border: 1px solid #00d4ff; background-color: rgba(0, 212, 255, 0.05); color: #00d4ff; font-weight: bold; width: 100%; height: 3.5em; }
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

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    u_info = STAFF_DATA[name]
    st.markdown(f"<h2>مرحباً، {name} 🛸</h2>", unsafe_allow_html=True)
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب", f"{u_info['salary']:,}")
    c2.metric("الخصم", f"{total_disc:,}")
    c3.metric("الصافي", f"{u_info['salary'] - total_disc + manual_bonuses:,}")

    st.divider()
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    shift_selected = "single"
    if u_info['type'] == 'double':
        shift_selected = st.radio("الوجبة:", ["الأولى", "الثانية"], horizontal=True)

    col_a, col_b = st.columns(2)
    
    if col_a.button("📥 تسجيل حضور"):
        t_ref = u_info['start'] if u_info['type'] == 'single' else (u_info['s1'] if shift_selected == "الأولى" else u_info['s2'])
        t_start = datetime.strptime(t_ref, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        disc = int((now - t_start).total_seconds() / 60 * LATE_RATE) if now > t_start + timedelta(minutes=5) else 0
        send_to_google(name, c_date, c_time, f"حضور ({shift_selected})", disc, 0)
        st.success("تم تسجيل الحضور")
        time.sleep(1); st.rerun()

    if col_b.button("📤 تسجيل انصراف"):
        send_to_google(name, c_date, c_time, f"انصراف ({shift_selected})", 0, 0)
        st.info("تم تسجيل الانصراف")
        time.sleep(1); st.rerun()

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h2>👑 Control Center</h2>", unsafe_allow_html=True)
    
    with st.expander("⏰ تعديل أوقات دوام الموظفين"):
        target = st.selectbox("الموظف:", list(STAFF_DATA.keys()))
        curr = STAFF_DATA[target]
        if curr['type'] == 'single':
            new_s = st.text_input("وقت الحضور:", value=curr['start'])
            new_e = st.text_input("وقت الانصراف:", value=curr['end'])
            if st.button(f"حفظ {target}"):
                st.session_state['staff_registry'][target].update({"start": new_s, "end": new_e})
                st.success("تم الحفظ")
        else:
            c1, c2 = st.columns(2)
            ns1 = c1.text_input("بداية 1:", value=curr['s1'])
            ne1 = c1.text_input("نهاية 1:", value=curr['e1'])
            ns2 = c2.text_input("بداية 2:", value=curr['s2'])
            ne2 = c2.text_input("نهاية 2:", value=curr['e2'])
            if st.button(f"حفظ وجبات {target}"):
                st.session_state['staff_registry'][target].update({"s1": ns1, "e1": ne1, "s2": ns2, "e2": ne2})
                st.success("تم التحديث")

    with st.expander("👤 إدارة الموظفين والرواتب"):
        mode = st.radio("العملية:", ["تعديل راتب", "إضافة موظف"], horizontal=True)
        if mode == "تعديل راتب":
            t_emp = st.selectbox("اختر الموظف:", list(STAFF_DATA.keys()), key="sal_edit")
            n_sal = st.number_input("الراتب الجديد:", value=STAFF_DATA[t_emp]['salary'])
            if st.button("تحديث الراتب"):
                st.session_state['staff_registry'][t_emp]['salary'] = n_sal
                st.success("تم التحديث")
        else:
            name_n = st.text_input("اسم الموظف الجديد:")
            type_n = st.selectbox("النوع:", ["single", "double"])
            if st.button("إضافة"):
                st.session_state['staff_registry'][name_n] = {"salary": 75000, "pass": "1234", "type": type_n, "start": "15:00", "end": "22:00"}
                st.success("تمت الإضافة")

    st.divider()
    df_raw = fetch_and_clean_data()
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.subheader("➕ مكافأة")
        e_m = st.selectbox("للموظف:", list(STAFF_DATA.keys()), key="m1")
        a_m = st.number_input("المبلغ:", step=1000, key="am1")
        if st.button("منح"):
            send_to_google(e_m, "مكافأة", "---", "مكافأة", 0, a_m)
            st.success("تم")
            
    with c_m2:
        st.subheader("🚫 غياب")
        e_g = st.selectbox("للموظف:", list(STAFF_DATA.keys()), key="g1")
        a_g = st.number_input("المبلغ:", value=15000, step=1000, key="ag1")
        if st.button("خصم"):
            send_to_google(e_g, "غياب", "---", "غياب", a_g, 0)
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

    st.sidebar.button("🚪 خروج", on_click=lambda: st.session_state.update({'auth': False}))
