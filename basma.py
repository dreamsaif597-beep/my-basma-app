import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# --- مخزن التاريخ للتصفير (لحل مشكلة التأخير) ---
if "reset_timestamp" not in st.session_state:
    st.session_state["reset_timestamp"] = datetime(2000, 1, 1)

def clean_name(name):
    if pd.isna(name): return ""
    return str(name).strip().replace("أ", "ا").replace("إ", "ا")

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": discount, 
        "entry.1151470082": overtime  
    }
    try: requests.post(FORM_URL, data=payload, timeout=5)
    except: pass

def get_total_discounts(name):
    try:
        # إضافة time.time() لضمان عدم قراءة نسخة قديمة (Cache)
        df = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
        df['data'] = pd.to_datetime(df['data']).dt.date
        df['timestamp'] = pd.to_datetime(df['data'].astype(str) + ' ' + df['time'].astype(str))
        
        # نأخذ التاريخ الأحدث بين (تاريخ آخر تصفية بالجدول) وبين (تاريخ ضغطة زر التصفير الحالية)
        resets = df[df['type'] == 'تصفية أسبوعية']
        if not resets.empty:
            table_reset = pd.to_datetime(resets['timestamp']).max()
        else:
            table_reset = pd.to_datetime("2000-01-01")
            
        final_reset = max(table_reset, st.session_state["reset_timestamp"])

        target = clean_name(name)
        mask = (df['name'].apply(clean_name) == target) & (df['timestamp'] >= final_reset)
        return int(df.loc[mask, 'discount'].sum())
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

# --- واجهة الموظف ---
if role == "موظف":
    user_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    password = st.sidebar.text_input("الرمز السري:", type="password")

    if password == STAFF_DATA[user_name]["pass"]:
        st.header(f"👋 أهلاً {user_name}")
        
        discounts = get_total_discounts(user_name)
        salary = STAFF_DATA[user_name]['salary']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("الراتب الكلي", f"{salary:,}")
        c2.metric("الخصومات", f"{discounts:,}", delta_color="inverse")
        c3.metric("صافي الخميس", f"{salary - discounts:,}")
        
        st.divider()
        now = datetime.now()
        if st.button("📥 تسجيل حضور"):
            start_t = STAFF_DATA[user_name]['start'] if STAFF_DATA[user_name]['type'] == 'single' else STAFF_DATA[user_name]['s1']
            diff = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(start_t, "%H:%M")).total_seconds() / 60
            disc = int(diff * 200) if diff > 5 else 0
            send_to_google(user_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "حضور", disc)
            st.success("تم تسجيل الحضور!")
            time.sleep(1)
            st.rerun()

        if st.button("📤 تسجيل انصراف"):
            send_to_google(user_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "انصراف", 0)
            st.info("تم تسجيل الانصراف.")

# --- واجهة المدير ---
elif role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة المدير")
        
        # رابط الجدول
        st.markdown(f"### [🔗 فتح جدول الردود الرئيسي](https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/edit#gid=1114343408)")

        # تسجيل غياب
        st.subheader("🚫 تسجيل غياب")
        absent_user = st.selectbox("الموظف الغائب:", list(STAFF_DATA.keys()))
        if st.button("خصم 15,000 غياب"):
            today = datetime.now()
            send_to_google(absent_user, today.strftime("%Y-%m-%d"), today.strftime("%H:%M:%S"), "غياب", 15000)
            st.error(f"تم الخصم من {absent_user}")
            time.sleep(1)
            st.rerun()

        st.divider()
        # عرض الكشف
        st.subheader("📊 كشف الرواتب (يوم الخميس)")
        if st.button("تحديث وعرض الجدول"):
            data_rows = []
            for n, d in STAFF_DATA.items():
                disc = get_total_discounts(n)
                data_rows.append({"الموظف": n, "الراتب": d['salary'], "الخصومات": disc, "الصافي": d['salary'] - disc})
            st.table(pd.DataFrame(data_rows).sort_values(by="الصافي", ascending=False))

        st.divider()
        # التصفير
        if st.button("🔄 تصفير الأسبوع بالكامل"):
            now = datetime.now()
            st.session_state["reset_timestamp"] = now # تصفير فوري في التطبيق
            send_to_google("النظام", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "تصفية أسبوعية", 0)
            st.balloons()
            st.success("تم التصفير! جميع الحسابات أصبحت صفر الآن.")
            time.sleep(1)
            st.rerun()
