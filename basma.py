import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# حفظ بيانات الموظفين والإعدادات في الـ session_state
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
PENALTY_RATE = st.session_state['penalty_rate']

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
    except: st.error("فشل الاتصال بجوجل")

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

# --- تحسين واجهة المستخدم ووضوح الخط ---
st.set_page_config(page_title="Al-Basma Smart System", layout="centered")

st.markdown("""
    <style>
    /* تحسين الخلفية العامة */
    .stApp {
        background: linear-gradient(135deg, #050505, #1a1a2e, #16213e);
    }
    
    /* فرض اللون الأبيض الناصع على جميع النصوص */
    html, body, [class*="st-"], .stMarkdown p, .stRadio label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* تحسين وضوح صناديق الإدخال والقوائم */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: #FFFFFF !important;
        border: 1px solid #00f2fe !important;
        border-radius: 10px !important;
    }

    /* جعل العناوين والـ Labels بارزة جداً */
    label p {
        font-weight: bold !important;
        font-size: 1.1rem !important;
        color: #00f2fe !important; /* لون فيروزي للتسميات لتسهيل القراءة */
    }

    /* تنسيق الأزرار */
    .stButton>button {
        border-radius: 15px;
        border: 2px solid #00f2fe;
        background: rgba(0, 242, 254, 0.15);
        color: #FFFFFF !important;
        font-weight: bold;
        height: 3em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #00f2fe;
        color: #000000 !important;
        box-shadow: 0 0 15px #00f2fe;
    }

    /* تحسين وضوح الـ Metrics (الراتب والخصم) */
    div[data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 1.8rem !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] p { color: #FFFFFF !important; }

    /* تحسين الجداول والبطاقات */
    .stTable { background-color: rgba(255,255,255,0.05); border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- تسجيل الدخول ---
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; text-shadow: 2px 2px 10px #000;'>💎 بصمة البسمة الذكية</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background: rgba(255,255,255,0.08); padding: 30px; border-radius: 20px; border: 1px solid rgba(0,242,254,0.3)'>", unsafe_allow_html=True)
        role = st.radio("نوع الصلاحية:", ["موظف", "المدير"], horizontal=True)
        
        if role == "موظف":
            user_sel = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
            user_pass = st.text_input("كلمة المرور الشخصية:", type="password")
            if st.button("دخول للنظام"):
                if user_pass == STAFF_DATA[user_sel]["pass"]:
                    st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
                    st.rerun()
                else: st.error("عذراً، الرمز السري غير صحيح")
        else:
            admin_pass = st.text_input("رمز الإدارة الرئيسي:", type="password")
            if st.button("فتح لوحة التحكم"):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("عذراً، الرمز السري غير صحيح")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# باقي الكود البرمجي (الموظف والمدير) يتبع نفس المنطق مع تطبيق الثيم الجديد...
# (للاختصار، قمت بتجهيز هذا الجزء ليعمل مباشرة مع الواجهة المحسنة)

with st.sidebar:
    st.markdown(f"<h3 style='color:#00f2fe'>👤 {st.session_state.get('user', 'المدير')}</h3>", unsafe_allow_html=True)
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.update({'auth': False})
        st.rerun()

if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp_info = STAFF_DATA[name]
    st.markdown(f"<h2 style='text-align: right; color: #FFFFFF;'>أهلاً بك، {name} ✨</h2>", unsafe_allow_html=True)
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = emp_info['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("الراتب", f"{salary:,}")
    col_m2.metric("الخصومات", f"{total_disc:,}")
    col_m3.metric("الصافي", f"{salary - total_disc + manual_bonuses:,}")

    st.markdown("<div style='background: rgba(255,255,255,0.07); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%
