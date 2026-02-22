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

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": discount, 
        "entry.1151470082": overtime  
    }
    try: requests.post(FORM_URL, data=payload)
    except: pass

def get_total_discounts(name):
    # إذا ضغط المدير تصفير للتو، نرجع 0 فوراً دون قراءة الجدول القديم
    if "force_zero" in st.session_state and st.session_state["force_zero"]:
        return 0
        
    try:
        # إضافة عامل زمني عشوائي للرابط لإجبار جوجل على إعطائنا أحدث بيانات
        timestamp_url = f"{SHEET_CSV_URL}&cache_bust={time.time()}"
        df = pd.read_csv(timestamp_url)
        df['data'] = pd.to_datetime(df['data']).dt.date
        
        reset_entries = df[df['type'] == 'تصفية أسبوعية']
        if not reset_entries.empty:
            last_reset_date = reset_entries['data'].max()
        else:
            last_reset_date = datetime(2000, 1, 1).date()

        target_name = clean_name(name)
        mask = (df['name'].apply(clean_name) == target_name) & (df['data'] >= last_reset_date)
        return int(df.loc[mask, 'discount'].sum())
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        # تصفير الحالة إذا دخل الموظف بعد التصفير
        total_discounts = get_total_discounts(selected_name)
        weekly_salary = STAFF_DATA[selected_name]['salary']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الكلي", f"{weekly_salary:,} د.ع")
        col_m2.metric("خصومات الأسبوع", f"{total_discounts:,} د.ع")
        col_m3.metric("صافي الخميس", f"{weekly_salary - total_discounts:,} د.ع")
        
        st.divider()
        # (بقية كود البصمة...)
        if st.button("📥 تسجيل حضور"):
            now = datetime.now()
            send_to_google(selected_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "حضور", 0, 0)
            st.success("تم التسجيل")
            st.rerun()

elif user_role == "المدير":
    admin_pass = st.sidebar.text_input("رمز المدير:", type="password")
    if admin_pass == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        # كشف الرواتب
        st.subheader("📊 كشف رواتب الأسبوع")
        if st.button("عرض الترتيب الحالي"):
            st.session_state["force_zero"] = False # إعادة القراءة من الجدول
            results = []
            for n, d in STAFF_DATA.items():
                dis = get_total_discounts(n)
                results.append({"الموظف": n, "الخصم": f"{dis:,}", "الصافي": d['salary']-dis})
            df_res = pd.DataFrame(results).sort_values(by="الصافي", ascending=False)
            st.table(df_res)

        st.divider()
        # التصفير مع حل مشكلة عدم الحذف الفوري
        if st.button("🔄 تصفير الأسبوع (حذف كل الخصومات)"):
            today = datetime.now().strftime("%Y-%m-%d")
            send_to_google("النظام", today, "00:00", "تصفية أسبوعية", 0, 0)
            
            # تفعيل التصفير الفوري في الذاكرة
            st.session_state["force_zero"] = True
            st.balloons()
            st.success("تم التصفير بنجاح! تم مسح الخصومات من العرض.")
            st.rerun()
