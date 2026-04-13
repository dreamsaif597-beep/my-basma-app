import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- التحكم بالدوام حسب الأيام ---
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

# --- ثيم "نيون جلاس" المتطور (التغيير الشامل هنا) ---
st.set_page_config(page_title="Al-Basma System", layout="centered")

st.markdown("""
    <style>
    /* خلفية متدرجة فخمة */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    /* تصميم الكروت الزجاجية */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
    }
    
    /* تحسين شكل الأزرار */
    .stButton>button {
        border-radius: 15px;
        border: none;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
        color: #ffffff;
    }

    /* أزرار الانصراف بلون مختلف */
    div[data-testid="column"]:nth-child(2) .stButton>button {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* العناوين */
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background: -webkit-linear-gradient(#fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* الجداول */
    .stTable {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* إخفاء القوائم غير الضرورية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name, "entry.786801446": data_val,
        "entry.2093200411": time_val, "entry.1043553703": type_val,
        "entry.1254543219": int(discount), "entry.1151470082": int(overtime)
    }
    try: requests.post(FORM_URL, data=payload, timeout=7)
    except: st.error("⚠️ فشل الاتصال")

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

# --- منطق الدخول ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center;'>AL-BASMA SYSTEM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البصمة الإلكتروني الذكي</p>", unsafe_allow_html=True)
    
    with st.container():
        role = st.tabs(["👤 دخول الموظفين", "🔐 الإدارة"])
        
        with role[0]:
            user_sel = st.selectbox("اختر الاسم:", list(STAFF_DATA.keys()))
            user_pass = st.text_input("كلمة المرور:", type="password", key="u_pass")
            if st.button("تسجيل الدخول", use_container_width=True):
                if user_pass == STAFF_DATA[user_sel]["pass"]:
                    st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
                    st.rerun()
                else: st.error("عذراً، الرمز غير صحيح")
                
        with role[1]:
            admin_pass = st.text_input("رمز المدير:", type="password", key="a_pass")
            if st.button("دخول لوحة التحكم", use_container_width=True):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("رمز الإدارة خاطئ")
    st.stop()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    st.markdown(f"<h3>أهلاً {name} ✨</h3>", unsafe_allow_html=True)
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = STAFF_DATA[name]['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    # عرض العدادات بتصميم الكروت
    m1, m2, m3 = st.columns(3)
    m1.metric("الراتب", f"{salary:,}")
    m2.metric("الخصومات", f"{total_disc:,}")
    m3.metric("الصافي", f"{salary - total_disc + manual_bonuses:,}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    now = get_iraq_time()
    day_name = now.strftime("%A")
    rules = WEEKLY_RULES.get(day_name)
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    # تحديد الشفت
    if STAFF_DATA[name]['type'] == 'double':
        shift_selected = st.select_slider("حدد الوجبة الحالية:", options=["الأولى", "الثانية"])
    else:
        shift_selected = "single"

    col_a, col_b = st.columns(2)
    
    if col_a.button("📥 بـصـمـة حـضـور", use_container_width=True):
        if STAFF_DATA[name]['type'] == 'single':
            t_ref = rules['start']
        else:
            t_ref = rules['s1'] if shift_selected == "الأولى" else rules['s2']
            
        t_start = datetime.strptime(t_ref, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        disc = int((now - t_start).total_seconds() / 60 * 100) if now > t_start + timedelta(minutes=5) else 0
        
        send_to_google(name, c_date, c_time, f"حضور ({shift_selected})", disc, 0)
        st.toast(f"تم الحضور بنجاح. الخصم: {disc:,}", icon="✅")
        time.sleep(1); st.cache_data.clear(); st.rerun()

    if col_b.button("📤 بـصـمـة انـصـراف", use_container_width=True):
        if STAFF_DATA[name]['type'] == 'single':
            t_ref_e = rules['end']
        else:
            t_ref_e = rules['e1'] if shift_selected == "الأولى" else rules['e2']
            
        t_end = datetime.strptime(t_ref_e, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        ov = int((now - t_end).total_seconds() / 60 * 100) if now > t_end + timedelta(minutes=1) else 0
        
        send_to_google(name, c_date, c_time, f"انصراف ({shift_selected})", 0, ov)
        st.toast("تم تسجيل الانصراف. مع السلامة!", icon="👋")
        time.sleep(1); st.cache_data.clear(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("🕒 سجل الحركات الأخير"):
        if not user_records.empty:
            view_df = user_records.copy()
            view_df['التوقيت'] = view_df['data'] + " " + view_df['time']
            view_df['المكافأة'] = view_df.apply(lambda x: x['overtime'] if x['type'] == "مكافأة" else 0, axis=1)
            st.dataframe(view_df[['التوقيت', 'type', 'discount', 'المكافأة']], use_container_width=True)

    with st.expander("📩 مركز الطلبات"):
        t_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ (للسلفة فقط)", min_value=0, step=5000)
        reason = st.text_area("ملاحظات")
        if st.button("إرسال الطلب الآن"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.success("تم إرسال الطلب بنجاح")

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h3>مدير النظام 🛡️</h3>", unsafe_allow_html=True)
    
    # اختصارات سريعة
    tab1, tab2, tab3 = st.tabs(["📊 الرواتب", "📩 الطلبات", "⚙️ الإعدادات"])
    
    df_raw = fetch_and_clean_data()

    with tab1:
        if st.button("تحديث وتحميل البيانات"):
            st.cache_data.clear(); st.rerun()
            
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))
        
        if st.button("⚠️ تصفير السجلات (نهاية الأسبوع)"):
            send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
            st.balloons(); st.rerun()

    with tab2:
        if not df_raw.empty:
            reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
            archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
            pending = reqs[~reqs['data'].isin(archived)]
            if pending.empty:
                st.info("لا توجد طلبات جديدة")
            for i, row in pending[::-1].iterrows():
                with st.expander(f"🔔 طلب {row['type']} من {row['name']}"):
                    st.write(f"التفاصيل: {row['data']}")
                    st.write(f"المبلغ المرتبط: {row['discount']:,}")
                    ca, cb = st.columns(2)
                    if ca.button("✅ موافقة", key=f"ok{i}"):
                        if "سلفة" in row['type']:
                            send_to_google(row['name'], f"سلفة مثبتة: {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.rerun()
                    if cb.button("❌ رفض", key=f"no{i}"):
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.rerun()

    with tab3:
        st.subheader("إدارة الموظفين")
        target = st.selectbox("اختر موظفاً للتعديل:", list(STAFF_DATA.keys()))
        new_s = st.number_input("تعديل الراتب:", value=STAFF_DATA[target]['salary'])
        if st.button("حفظ التعديلات"):
            st.session_state['staff_registry'][target]['salary'] = new_s
            st.success("تم تحديث الراتب")

# سحاب جانبي للخروج
st.sidebar.markdown("---")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.update({'auth': False})
    st.rerun()
