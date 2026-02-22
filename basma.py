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

# دالة تنظيف الأسماء
def clean_name(name):
    if pd.isna(name): return ""
    return str(name).strip().replace("أ", "ا").replace("إ", "ا")

# دالة الإرسال إلى جوجل
def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": discount, 
        "entry.1151470082": overtime  
    }
    try:
        requests.post(FORM_URL, data=payload)
    except:
        st.error("فشل في الاتصال بجوجل")

# دالة حساب الخصومات
def get_total_discounts(name):
    try:
        # كسر الكاش لضمان تحديث البيانات من جوجل
        t_url = f"{SHEET_CSV_URL}&cache={time.time()}"
        df = pd.read_csv(t_url)
        df['data'] = pd.to_datetime(df['data']).dt.date
        
        # البحث عن آخر تصفية
        resets = df[df['type'] == 'تصفية أسبوعية']
        last_reset = resets['data'].max() if not resets.empty else datetime(2000,1,1).date()

        target = clean_name(name)
        mask = (df['name'].apply(clean_name) == target) & (df['data'] >= last_reset)
        return int(df.loc[mask, 'discount'].sum())
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

user_role = st.sidebar.radio("الدخول كـ:", ["موظف", "المدير"])

# --- واجهة الموظف ---
if user_role == "موظف":
    name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    pw = st.sidebar.text_input("الرمز السري:", type="password")

    if pw == STAFF_DATA[name]["pass"]:
        st.header(f"👋 أهلاً {name}")
        
        # الحساب المالي
        weekly_sal = STAFF_DATA[name]['salary']
        discounts = get_total_discounts(name)
        
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("الراتب الكلي", f"{weekly_sal:,}")
        c_m2.metric("الخصومات", f"{discounts:,}")
        c_m3.metric("الصافي", f"{weekly_sal - discounts:,}")
        
        st.divider()
        st.subheader("⏱️ البصمة")
        now = datetime.now()
        curr_d, curr_t = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[name]
            start_t = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(start_t, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            disc = int(diff * 200) if diff > 5 else 0
            
            send_to_google(name, curr_d, curr_t, "حضور", disc)
            st.success(f"تم تسجيل الحضور. الخصم: {disc:,}")
            time.sleep(1)
            st.rerun()

        if col_btn2.button("📤 تسجيل انصراف"):
            send_to_google(name, curr_d, curr_t, "انصراف", 0)
            st.info("تم تسجيل الانصراف بنجاح")

# --- واجهة المدير ---
elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة المدير")

        # 1. تسجيل غياب
        st.subheader("🚫 تسجيل غياب يدوي")
        abs_name = st.selectbox("الموظف الغائب:", list(STAFF_DATA.keys()))
        if st.button("خصم غياب (15,000)"):
            today = datetime.now().strftime("%Y-%m-%d")
            send_to_google(abs_name, today, "00:00", "غياب", 15000)
            st.error(f"تم خصم الغياب من {abs_name}")
            time.sleep(1)
            st.rerun()

        st.divider()

        # 2. كشف الرواتب والترتيب
        st.subheader("📊 كشف رواتب الخميس")
        if st.button("عرض وترتيب الرواتب"):
            sal_list = []
            for n, d in STAFF_DATA.items():
                disc = get_total_discounts(n)
                sal_list.append({"الموظف": n, "الراتب": d['salary'], "الخصم": disc, "الصافي": d['salary'] - disc})
            
            df_final = pd.DataFrame(sal_list).sort_values(by="الصافي", ascending=False)
            st.table(df_final)

        st.divider()

        # 3. التصفير
        st.subheader("🔄 تصفير الأسبوع")
        if st.button("تصفير وبدء أسبوع جديد للجميع"):
            today = datetime.now().strftime("%Y-%m-%d")
            # إرسال سطر التصفية
            send_to_google("نظام", today, "00:00", "تصفية أسبوعية", 0)
            st.balloons()
            st.success("تم إرسال أمر التصفير. انتظر 5 ثوانٍ للتحديث...")
            time.sleep(2)
            st.rerun()
