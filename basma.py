import streamlit as st
from datetime import datetime
import requests

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# دالة الإرسال بالأرقام الدقيقة من رابطك الأخير
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

# --- واجهة الدخول ---
st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        st.metric("الراتب الأسبوعي", f"{STAFF_DATA[selected_name]['salary']:,} د.ع")
        
        now = datetime.now()
        c_date = now.strftime("%Y-%m-%d")
        c_time = now.strftime("%H:%M:%S")

        st.divider()
        st.subheader("⏱️ تسجيل البصمة")
        col1, col2 = st.columns(2)
        
        if col1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            official_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(official_start, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            
            discount = int(diff * 200) if diff > 5 else 0
            if discount > 0: st.error(f"تأخير {int(diff)} دقيقة. الخصم: {discount:,} د.ع")
            else: st.success("حضور في الوقت المحدد!")
            
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.balloons()

        if col2.button("📤 تسجيل انصراف"):
            st.info("تم تسجيل الانصراف")
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)

        st.divider()
        with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
            type_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
            if st.button("إرسال الطلب"):
                send_to_google(selected_name, c_date, c_time, f"طلب {type_req}", 0, 0)
                st.warning(f"تم إرسال طلب {type_req} للمدير")

elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("📊 لوحة تحكم المدير")
        sheet_url = "https://docs.google.com/spreadsheets/d/1oS3jJ7Z6PhvK3aB5H4bjfNuR2Qku2QwGLvw4Jl9PXwI/edit#gid=1114343408"
        st.markdown(f"### [🔗 اضغط هنا لفتح جدول البصمات (تأكد من فتح صفحة Form_Responses)]({sheet_url})")
        
        st.divider()
        st.subheader("👥 كشف الرواتب")
        for staff, info in STAFF_DATA.items():
            st.write(f"**{staff}**: الراتب {info['salary']:,} د.ع")
        
        if st.button("💰 تصفية حسابات الخميس"):
            st.success("تم تأشير التصفية")
