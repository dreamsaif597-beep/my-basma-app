import streamlit as st
from datetime import datetime
import requests

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"

# بيانات الموظفين (الشفتات والرواتب)
STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# وظيفة الإرسال للجدول بالـ IDs الصحيحة
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

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # ميزة الراتب اليومي
        weekly_salary = STAFF_DATA[selected_name]['salary']
        daily_salary = int(weekly_salary / 7)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,} د.ع")
        col_m2.metric("يوميتك (الصافي)", f"{daily_salary:,} د.ع")
        
        st.divider()
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
                st.info(f"الصافي اليوم بعد الخصم: {daily_salary - discount:,} د.ع")
            else:
                st.success(f"تم الحضور في الوقت المحدد! الصافي: {daily_salary:,} د.ع")
            
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.balloons()

        if c2.button("📤 تسجيل انصراف"):
            st.info(f"تم تسجيل الانصراف: {c_time}")
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)

        st.divider()
        with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
            t_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
            if st.button("إرسال الطلب"):
                send_to_google(selected_name, c_date, c_time, f"طلب {t_req}", 0, 0)
                st.warning(f"تم إرسال طلب {t_req} للمدير بنجاح")

elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        sheet_url = "https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/edit#gid=1114343408"
        st.markdown(f"### [🔗 فتح جدول البصمات (صفحة Form_Responses)]({sheet_url})")
        
        st.divider()
        st.subheader("👥 كشف الرواتب العام")
        for staff, info in STAFF_DATA.items():
            d_sal = int(info['salary'] / 7)
            st.write(f"**{staff}**: أسبوعي {info['salary']:,} | يومي {d_sal:,} د.ع")
        
        st.divider()
        if st.button("💰 تصفية حسابات الخميس"):
            st.success("تم تسجيل نهاية الدورة الأسبوعية")
            st.balloons()
