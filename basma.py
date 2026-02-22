import streamlit as st
from datetime import datetime

# --- البيانات الثابتة ---
ADMIN_PASSWORD = "5566"
STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30"},
}

st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

# فرضنا وجود قيم افتراضية للحسابات (ستأتي من الجدول لاحقاً)
discount = 0  # الخصومات
overtime = 0  # الإضافي

if user_role == "موظف":
    name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    pw = st.sidebar.text_input("الرمز السري:", type="password")
    
    if pw == STAFF_DATA[name]["pass"]:
        st.header(f"👋 أهلاً {name}")
        
        # حسبة الموظف: الراتب - الخصم فقط (لا يرى الأوفر تايم)
        net_salary_employee = STAFF_DATA[name]['salary'] - discount
        
        col1, col2 = st.columns(2)
        col1.metric("الراتب الأساسي", f"{STAFF_DATA[name]['salary']:,} د.ع")
        col2.metric("الصافي (بعد الخصومات)", f"{net_salary_employee:,} د.ع")
        
        if discount > 0:
            st.error(f"لديك خصومات بقيمة: {discount:,} د.ع")
        
        st.divider()
        if st.button("📥 بصمة حضور"):
            st.success("تم تسجيل الحضور") # هنا سيتم الإرسال للجدول

elif user_role == "المدير":
    admin_pw = st.sidebar.text_input("رمز المدير:", type="password")
    if admin_pw == ADMIN_PASSWORD:
        st.header("📊 لوحة تحكم المدير")
        
        # حسبة المدير: الراتب - الخصم + الأوفرتايم
        st.subheader("💰 كشف الرواتب التفصيلي")
        for staff, data in STAFF_DATA.items():
            total_net_admin = data['salary'] - discount + overtime
            with st.expander(f"تفاصيل راتب: {staff}"):
                st.write(f"الراتب الأساسي: {data['salary']:,}")
                st.write(f"الخصومات: {discount:,}")
                st.write(f"الإضافي (أوفرتايم): {overtime:,}")
                st.success(f"الصافي النهائي للمدير: {total_net_admin:,} د.ع")
