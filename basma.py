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

def clean_name(name):
    if pd.isna(name): return ""
    return str(name).strip().replace("أ", "ا").replace("إ", "ا")

def send_to_google(name, data_val, time_val, type_val, discount=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": discount
    }
    try: requests.post(FORM_URL, data=payload, timeout=5)
    except: pass

def get_total_discounts(name):
    try:
        # كسر الكاش لجلب أحدث بيانات
        df = pd.read_csv(f"{SHEET_CSV_URL}&cache={time.time()}")
        df['data'] = pd.to_datetime(df['data']).dt.date
        
        # إيجاد تاريخ آخر تصفير في الجدول
        resets = df[df['type'] == 'تصفية أسبوعية']
        if not resets.empty:
            last_reset_date = resets['data'].max()
        else:
            last_reset_date = datetime(2000, 1, 1).date()

        target = clean_name(name)
        # نحسب الخصومات التي تاريخها يساوي أو بعد تاريخ آخر تصفية
        mask = (df['name'].apply(clean_name) == target) & (df['data'] >= last_reset_date)
        return int(df.loc[mask, 'discount'].sum())
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if role == "موظف":
    u_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    u_pass = st.sidebar.text_input("الرمز:", type="password")

    if u_pass == STAFF_DATA[u_name]["pass"]:
        st.header(f"👋 أهلاً {u_name}")
        dis = get_total_discounts(u_name)
        sal = STAFF_DATA[u_name]['salary']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("الراتب الكلي", f"{sal:,}")
        c2.metric("الخصومات", f"{dis:,}")
        c3.metric("الصافي", f"{sal - dis:,}")
        
        st.divider()
        now = datetime.now()
        if st.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[u_name]
            start_t = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(start_t, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            disc = int(diff * 200) if diff > 5 else 0
            
            send_to_google(u_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "حضور", disc)
            st.success(f"تم تسجيل الحضور. الخصم: {disc:,}")
            time.sleep(2) # انتظار قليل للتأكد من وصول البيانات لجوجل
            st.rerun()

        if st.button("📤 تسجيل انصراف"):
            send_to_google(u_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "انصراف", 0)
            st.info("تم تسجيل الانصراف.")

elif role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة المدير")
        st.markdown("[🔗 فتح الجدول الرئيسي](https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/edit#gid=1114343408)")

        # غياب
        abs_u = st.selectbox("الموظف الغائب:", list(STAFF_DATA.keys()))
        if st.button("خصم 15,000 غياب"):
            today = datetime.now()
            send_to_google(abs_u, today.strftime("%Y-%m-%d"), today.strftime("%H:%M:%S"), "غياب", 15000)
            st.error(f"تم الخصم من {abs_u}")
            time.sleep(2)
            st.rerun()

        st.divider()
        # عرض الكشف
        if st.button("📊 عرض كشف الرواتب والترتيب"):
            rows = []
            for n, d in STAFF_DATA.items():
                disc = get_total_discounts(n)
                rows.append({"الموظف": n, "الراتب": d['salary'], "الخصم": disc, "الصافي": d['salary'] - disc})
            st.table(pd.DataFrame(rows).sort_values(by="الصافي", ascending=False))

        st.divider()
        # التصفير
        if st.button("🔄 تصفير الأسبوع"):
            today = datetime.now().strftime("%Y-%m-%d")
            send_to_google("النظام", today, "23:59:59", "تصفية أسبوعية", 0)
            st.balloons()
            st.success("تم التصفير. سيظهر الصفر للجميع خلال لحظات.")
            time.sleep(2)
            st.rerun()
