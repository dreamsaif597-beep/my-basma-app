import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- 1. الإعدادات الأساسية وروابط الربط ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- 2. إدارة البيانات (Session State) ---
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
    st.session_state['penalty_rate'] = 100 # معدل الخصم الافتراضي (يمكن للمدير تغييره)

STAFF_DATA = st.session_state['staff_registry']

# --- 3. الدوال البرمجية ---
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
    except: st.error("⚠️ فشل الاتصال بجوجل شيت")

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

# --- 4. واجهة المستخدم الرسومية (UI Design) ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
    }}
    .main-card {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 210, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }}
    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 12px;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.6);
    }}
    div[data-testid="stMetricValue"] {{ color: #00d2ff !important; font-size: 28px; }}
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- 5. منطق تسجيل الدخول ---
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #00d2ff;'>💎 بصمة البسمة الذكية</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        role = st.radio("من فضلك اختر نوع الدخول:", ["موظف", "الإدارة"], horizontal=True)
        if role == "موظف":
            u_name = st.selectbox("اختر اسمك من القائمة:", list(STAFF_DATA.keys()))
            u_pass = st.text_input("ادخل رمزك السري:", type="password")
            if st.button("دخول الموظف"):
                if u_pass == STAFF_DATA[u_name]["pass"]:
                    st.session_state.update({'auth':True, 'user':u_name, 'role':"موظف"})
                    st.rerun()
                else: st.error("❌ الرمز السري غير صحيح")
        else:
            a_pass = st.text_input("رمز المدير الخاص:", type="password")
            if st.button("دخول لوحة التحكم"):
                if a_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("❌ رمز المدير غير صحيح")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('user', 'المدير')}")
    st.divider()
    if st.button("🚪 تسجيل خروج"):
        st.session_state.update({'auth': False})
        st.rerun()
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear(); st.rerun()

# --- 7. واجهة الموظف (حضور/انصراف/شفتات) ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp = STAFF_DATA[name]
    st.markdown(f"## 🌟 طاب يومك، {name}")
    
    df = fetch_and_clean_data()
    user_rec = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    # حساب المستحقات
    sal = emp['salary']
    disc = int(user_rec['discount'].sum())
    bon = int(user_rec[user_rec['type'] == "مكافأة"]['overtime'].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("الراتب", f"{sal:,}")
    col2.metric("الخصومات", f"{disc:,}")
    col3.metric("الصافي", f"{sal - disc + bon:,}")

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    # نظام الشفتات الذكي
    target_start = ""
    if emp['type'] == 'double':
        st.write("📍 **نظام شفتات:** يرجى اختيار الشفت الحالي للبصمة")
        shift_opt = st.radio("الشفت:", ["الوجبة الأولى", "الوجبة الثانية"], horizontal=True)
        target_start = emp['s1'] if shift_opt == "الوجبة الأولى" else emp['s2']
        attendance_type = f"حضور ({shift_opt})"
    else:
        target_start = emp['start']
        attendance_type = "حضور"

    ca, cb = st.columns(2)
    if ca.button("📥 تسجيل بصمة حضور"):
        t_target = datetime.strptime(target_start, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        delay_min = (now - t_target).total_seconds() / 60
        penalty = int(delay_min * st.session_state['penalty_rate']) if delay_min > 5 else 0
        send_to_google(name, c_date, c_time, attendance_type, penalty, 0)
        st.success(f"✅ تم الحضور بنجاح. الخصم المحسوب: {penalty:,}")
        st.cache_data.clear(); time.sleep(1); st.rerun()

    if cb.button("📤 تسجيل بصمة انصراف"):
        send_to_google(name, c_date, c_time, "انصراف", 0, 0)
        st.info("✅ تم تسجيل الانصراف. نراك غداً")
        st.cache_data.clear(); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📝 تقديم طلب (سلفة / إجازة)"):
        t_req = st.selectbox("نوع الطلب:", ["سلفة", "إجازة"])
        amt_req = st.number_input("المبلغ (للسلف فقط):", min_value=0, step=5000)
        reason = st.text_input("السبب أو التاريخ المطلوب:")
        if st.button("إرسال الطلب للإدارة"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("⏳ تم إرسال الطلب وبانتظار موافقة المدير")

# --- 8. واجهة المدير (التحكم الكامل) ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h2 style='text-align: center; color: #00d2ff;'>👑 لوحة تحكم المدير</h2>", unsafe_allow_html=True)
    df_raw = fetch_and_clean_data()

    # أ. التحكم بالمعادلة (يدوياً)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("⚙️ معادلة الخصم التلقائي")
        st.session_state['penalty_rate'] = st.number_input("مبلغ الخصم لكل دقيقة تأخير (دينار):", value=st.session_state['penalty_rate'], step=25)
        st.markdown('</div>', unsafe_allow_html=True)

    # ب. قسم الطلبات (الموافقة والرفض)
    st.subheader("📩 طلبات الموظفين الواردة")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived)]
        
        if pending.empty:
            st.info("لا توجد طلبات معلقة حالياً")
        else:
            for i, row in pending.iterrows():
                with st.container():
                    st.markdown(f"""<div class="main-card" style="border-left: 5px solid #00d2ff;">
                        <b>الموظف:</b> {row['name']} | <b>النوع:</b> {row['type']} <br>
                        <b>التفاصيل:</b> {row['data']} | <b>المبلغ:</b> {row['discount']:,} دينار
                    </div>""", unsafe_allow_html=True)
                    cy, cn = st.columns(2)
                    if cy.button("✅ موافقة", key=f"y_{i}"):
                        if "سلفة" in row['type']:
                            send_to_google(row['name'], f"سلفة معتمدة: {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()
                    if cn.button("❌ رفض", key=f"n_{i}"):
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()

    st.divider()

    # ج. إدارة الموظفين (تعديل الأوقات والرواتب)
    with st.expander("👥 إدارة سجل الموظفين والإعدادات"):
        target = st.selectbox("اختر الموظف لتعديل بياناته:", list(STAFF_DATA.keys()))
        curr = STAFF_DATA[target]
        new_sal = st.number_input("الراتب الأسبوعي:", value=curr['salary'])
        new_pass = st.text_input("رمز الدخول:", value=curr['pass'])
        
        if curr['type'] == 'single':
            c1, c2 = st.columns(2)
            ts = c1.text_input("وقت الحضور:", curr['start'])
            te = c2.text_input("وقت الانصراف:", curr['end'])
            if st.button("تحديث بيانات الدوام المنفرد"):
                st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_pass, "start":ts, "end":te})
                st.success("تم الحفظ")
        else:
            c1, c2, c3, c4 = st.columns(4)
            v1, v2, v3, v4 = c1.text_input("حضور 1", curr['s1']), c2.text_input("انصراف 1", curr['e1']), c3.text_input("حضور 2", curr['s2']), c4.text_input("انصراف 2", curr['e2'])
            if st.button("تحديث بيانات الدوام المزدوج"):
                st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_pass, "s1":v1, "e1":v2, "s2":v3, "e2":v4})
                st.success("تم الحفظ")

    # د. كشف الرواتب والمكافآت اليدوية
    st.subheader("📊 جدول الرواتب الصافية")
    if not df_raw.empty:
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        payroll = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            payroll.append({"الموظف": n, "الراتب الأساسي": info['salary'], "الخصومات": d, "المكافآت": o, "الصافي النهائي": info['salary'] - d + o})
        st.table(pd.DataFrame(payroll))

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("### ➕ إضافة مكافأة")
        e_b = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="b_emp")
        a_b = st.number_input("المبلغ:", step=1000, key="b_amt")
        if st.button("تأكيد المكافأة"):
            send_to_google(e_b, "مكافأة إدارية", "---", "مكافأة", 0, a_b)
            st.rerun()
    with col_m2:
        st.markdown("### 🚫 تسجيل خصم/غياب")
        e_g = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="g_emp")
        a_g = st.number_input("مبلغ الخصم:", value=15000, step=1000, key="g_amt")
        if st.button("تأكيد الخصم"):
            send_to_google(e_g, "خصم يدوي", "---", "غياب", a_g, 0)
            st.rerun()

    st.divider()
    if st.button("⚠️ تصفية وأرشفة السجلات الأسبوعية"):
        send_to_google("النظام", "تصفية", "00:00", "تصفية أسبوعية", 0, 0)
        st.balloons(); st.cache_data.clear(); st.rerun()
