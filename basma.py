import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- سجل الموظفين مع أوقاتهم الخاصة (القيمة الافتراضية) ---
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

# --- استايل الحداثة ---
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

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    user_info = STAFF_DATA[name]
    st.markdown(f"<h2>مرحباً، {name} 🛸</h2>", unsafe_allow_html=True)
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = user_info['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب الأساسي", f"{salary:,}")
    c2.metric("إجمالي الخصم", f"{total_disc:,}")
    c3.metric("الصافي المستحق", f"{salary - total_disc + manual_bonuses:,}")

    st.divider()
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    shift_selected = "single"
    if user_info['type'] == 'double':
        shift_selected = st.radio("اختر الوجبة الحالية:", ["الأولى", "الثانية"], horizontal=True)

    col_a, col_b = st.columns(2)
    
    if col_a.button("📥 تسجيل حضور"):
        # جلب وقت الحضور المخصص لهذا الموظف
        t_ref = user_info['start'] if user_info['type'] == 'single' else (user_info['s1'] if shift_selected == "الأولى" else user_info['s2'])
        t_start = datetime.strptime(t_ref, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        
        disc = int((now - t_start).total_seconds() / 60 * LATE_RATE) if now > t_start + timedelta(minutes=5) else 0
        
        send_to_google(name, c_date, c_time, f"حضور ({shift_selected})", disc, 0)
        st.success(f"تمت البصمة. وقتك المطلوب: {t_ref}. الخصم: {disc:,}")
        time.sleep(1); st.cache_data.clear(); st.rerun()

    if col_b.button("📤 تسجيل انصراف"):
        t_ref_e = user_info['end'] if user_info['type'] == 'single' else (user_info['e1'] if shift_selected == "الأولى" else user_info['e2'])
        t_end = datetime.strptime(t_ref_e, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        
        ov = int((now - t_end).total_seconds() / 60 * LATE_RATE) if now > t_end + timedelta(minutes=1) else 0
        
        send_to_google(name, c_date, c_time, f"انصراف ({shift_selected})", 0, ov)
        st.info(f"تم الانصراف. وقتك المطلوب: {t_ref_e}")
        time.sleep(1); st.cache_data.clear(); st.rerun()

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h2>👑 Control Center</h2>", unsafe_allow_html=True)
    
    # --- قسم التحكم بالأوقات (الطلب الجديد) ---
    with st.expander("⏰ تعديل أوقات دوام الموظفين"):
        st.info("قم بتعديل وقت الحضور والانصراف لكل موظف بشكل مستقل.")
        emp_to_edit = st.selectbox("اختر الموظف للتعديل:", list(STAFF_DATA.keys()))
        curr_data = STAFF_DATA[emp_to_edit]
        
        if curr_data['type'] == 'single':
            new_s = st.text_input("وقت الحضور (مثل 15:00):", value=curr_data['start'])
            new_e = st.text_input("وقت الانصراف (مثل 22:00):", value=curr_data['end'])
            if st.button(f"حفظ أوقات {emp_to_edit}"):
                st.session_state['staff_registry'][emp_to_edit]['start'] = new_s
                st.session_state['staff_registry'][emp_to_edit]['end'] = new_e
                st.success(f"تم حفظ وقت {emp_to_edit}")
                st.rerun()
        else:
            c1, c2 = st.columns(2)
            ns1 = c1.text_input("بداية الوجبة 1:", value=curr_data['s1'])
            ne1 = c1.text_input("نهاية الوجبة 1:", value=curr_data['e1'])
            ns2 = c2.text_input("بداية الوجبة 2:", value=curr_data['s2'])
            ne2 = c2.text_input("نهاية الوجبة 2:", value=curr_data['e2'])
            if st.button(f"حفظ وجبات {emp_to_edit}"):
                st.session_state['staff_registry'][emp_to_edit].update({"s1":ns1, "e1":ne1, "s2":ns2, "e2":ne2})
                st.success("تم تحديث الوجبات")
                st.rerun()

    with st.expander("⚙️ إعدادات الحساب (معدل الخصم)"):
        st.write(f"المعدل الحالي: {st.session_state['late_rate']} دينار/دقيقة")
        new_rate = st.number_input("تعديل الخصم:", value=st.session_state['late_rate'], step=10)
        if st.button("تحديث المعدل"):
            st.session_state['late_rate'] = new_rate
            st.success("تم التحديث")
            st.rerun()

    st.divider()
    # بقية كود المدير (المكافآت، الغياب، التقرير)
    df_raw = fetch_and_clean_data()
    
    st.subheader("📊 تقرير سريع")
    if st.button("عرض الرواتب"):
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))

    if st.button("🔄 تصفير البيانات"):
        send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.balloons(); st.rerun()
