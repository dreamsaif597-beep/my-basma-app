import streamlit as st
from datetime import datetime
import requests
import pandas as pd

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

# ميزة التصفية: حفظ تاريخ بداية الأسبوع الجديد في "ذاكرة المتصفح"
if "last_reset" not in st.session_state:
    st.session_state["last_reset"] = "2000-01-01" # تاريخ قديم جداً كبداية

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
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # تحويل عمود التاريخ لنوع تاريخ لكي نستطيع المقارنة
        df['data'] = pd.to_datetime(df['data']).dt.date
        reset_date = datetime.strptime(st.session_state["last_reset"], "%Y-%m-%d").date()
        
        # تصفية: فقط الأسماء المطابقة + التواريخ التي بعد تاريخ التصفية
        mask = (df['name'].str.strip() == name) & (df['data'] >= reset_date)
        user_discounts = df.loc[mask, 'discount'].sum()
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
        
        weekly_salary = STAFF_DATA[selected_name]['salary']
        total_discounts = get_total_discounts(selected_name)
        final_salary = weekly_salary - total_discounts
        
        st.subheader("💰 كشف حسابك للأسبوع الحالي")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الكلي", f"{weekly_salary:,} د.ع")
        col_m2.metric("خصومات الأسبوع", f"{total_discounts:,} د.ع", delta_color="inverse")
        col_m3.metric("صافي الخميس", f"{final_salary:,} د.ع")
        
        st.divider()
        st.subheader("⏱️ تسجيل البصمة")
        now = datetime.now()
        c_date = now.strftime("%Y-%m-%d")
        c_time = now.strftime("%H:%M:%S")

        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            off_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(off_start, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            
            discount = int(diff * 200) if diff > 5 else 0
            if discount > 0:
                st.error(f"تأخير {int(diff)} دقيقة. الخصم: {discount:,} د.ع")
            else:
                st.success("تم الحضور في الوقت!")
            
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            st.info(f"تم الانصراف: {c_time}")
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)

elif user_role == "المدير":
    admin_pass = st.sidebar.text_input("رمز المدير:", type="password")
    if admin_pass == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/edit#gid=1114343408"
        st.markdown(f"### [🔗 فتح جدول الردود الرئيسي]({sheet_url})")
        
        st.divider()
        st.subheader("👥 ملخص رواتب الأسبوع الحالي")
        for name, data in STAFF_DATA.items():
            dis = get_total_discounts(name)
            st.write(f"**{name}**: الصافي {data['salary'] - dis:,} د.ع (خصم الأسبوع: {dis:,})")
        
        st.divider()
        # زر التصفية الجديد
        if st.button("🗑️ تصفير لبدء أسبوع جديد"):
            st.session_state["last_reset"] = datetime.now().strftime("%Y-%m-%d")
            st.balloons()
            st.success(f"تم تصفير العدادات. الأسبوع الجديد يبدأ من تاريخ اليوم: {st.session_state['last_reset']}")
            st.rerun()
