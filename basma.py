import streamlit as st
from datetime import datetime
import requests

# --- المعلومات الأساسية (التي لا تتغير) ---
ADMIN_PASSWORD = "5566"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# --- وظيفة إرسال البيانات للجدول (تستخدم رابط Google Form) ---
def send_to_google(name, status, discount=0, overtime=0):
    # هنا ستضع رابط الفورم الخاص بك لاحقاً
    form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"
    data = {
        "entry.123456": name,      # استبدل الأرقام بـ Entry ID من الفورم
        "entry.789012": status,
        "entry.345678": discount,
        "entry.901234": overtime
    }
    try:
        requests.post(form_url, data=data)
    except:
        pass

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

# --- واجهة تسجيل الدخول ---
st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # فرضنا قيم مؤقتة حتى يكتمل الربط
        total_discount = 0 
        
        # عرض الراتب للموظف (بدون أوفرتايم)
        net_for_staff = STAFF_DATA[selected_name]['salary'] - total_discount
        
        col1, col2 = st.columns(2)
        col1.metric("الراتب الأسبوعي", f"{STAFF_DATA[selected_name]['salary']:,} د.ع")
        col2.metric("الصافي (بعد الخصم)", f"{net_for_staff:,} د.ع")
        
        st.divider()
        st.subheader("⏱️ تسجيل البصمة")
        c1, c2 = st.columns(2)
        
        if c1.button("📥 تسجيل حضور"):
            now = datetime.now().strftime("%H:%M")
            st.success(f"تم تسجيل حضورك الساعة {now}")
            st.balloons()
            # استدعاء دالة الإرسال
            send_to_google(selected_name, "حضور")

        if c2.button("📤 تسجيل انصراف"):
            st.info("تم تسجيل الانصراف")
            send_to_google(selected_name, "انصراف")

        st.divider()
        with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
            req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
            if st.button("إرسال الطلب"):
                st.warning("تم الإرسال للمدير")

elif user_role == "المدير":
    admin_input = st.sidebar.text_input("رمز دخول المدير:", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.header("📊 لوحة تحكم المدير")
        
        # حسابات المدير (راتب - خصم + إضافي)
        st.subheader("👥 كشف الرواتب العام")
        for staff, info in STAFF_DATA.items():
            # حسبة افتراضية للمثال
            final_net = info['salary'] - 0 + 0 
            st.write(f"**{staff}**: الصافي للمدير (مع الإضافي) = {final_net:,} د.ع")
            
        if st.button("💰 تصفية حسابات الخميس"):
            st.balloons()
            st.success("تم تصفير الحسابات")
