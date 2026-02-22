import streamlit as st
from datetime import datetime
import requests
import pandas as pd # أضفنا هذه المكتبة لقراءة الجدول

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
# رابط الجدول بصيغة CSV للقراءة منه (مهم جداً لعرض الراتب النهائي)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/export?format=csv&gid=1114343408"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

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

# دالة لجلب مجموع الخصومات للموظف من الجدول
def get_total_discounts(name):
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # تصفية الجدول حسب اسم الموظف وجمع عمود الخصم
        user_discounts = df[df['name'] == name]['discount'].sum()
        return int(user_discounts)
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # ميزة الراتب اليومي والأسبوعي
        weekly_salary = STAFF_DATA[selected_name]['salary']
        total_discounts = get_total_discounts(selected_name)
        final_salary = weekly_salary - total_discounts
        
        st.subheader("💰 كشف حسابك الأسبوعي")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الكلي", f"{weekly_salary:,} د.ع")
        col_m2.metric("مجموع الخصومات", f"{total_discounts:,} د.ع", delta_color="inverse")
        col_m3.metric("الصافي (يوم الخميس)", f"{final_salary:,} د.ع")
        
        st.divider()
        # ... تكملة كود البصمة (نفس الكود السابق) ...
        st.subheader("⏱️ تسجيل البصمة")
        now = datetime.now()
        c_date = now.strftime("%Y-%m-%d")
        c_time = now.strftime("%H:%M:%S")

        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            official_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(official_start, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            
            discount = int(diff * 200) if diff > 5 else 0
            if discount > 0:
                st.error(f"تأخير {int(diff)} دقيقة. الخصم: {discount:,} د.ع")
            else:
                st.success(f"تم الحضور في الوقت المحدد!")
            
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.rerun() # تحديث الصفحة لظهار الخصم الجديد في المجموع

        if c2.button("📤 تسجيل انصراف"):
            st.info(f"تم تسجيل الانصراف: {c_time}")
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)
            
        # ... بقية الأزرار (إجازة/سلفة ولوحة المدير) ...
