import streamlit as st
import pandas as pd
from datetime import datetime, time

# إعدادات النظام وقواعد الحساب
STRICT_TIME_LIMIT = 5  # دقائق السماح
LATE_PENALTY_PER_MIN = 200 # خصم الدقيقة
OVERTIME_BONUS_PER_MIN = 100 # إضافي الدقيقة

# بيانات الموظفين (الرواتب والشفتات كما أرسلتها)
EMPLOYEES = {
    "فؤاد": {"salary": 165000, "shifts": [("10:20", "15:00"), ("17:20", "22:00")]},
    "ياسر": {"salary": 115000, "shifts": [("10:00", "13:00"), ("15:00", "23:00")]},
    "أمير": {"salary": 115000, "shifts": [("16:00", "23:00")]},
    "حارث": {"salary": 135000, "shifts": [("15:00", "22:00")]},
    "صادق": {"salary": 75000, "shifts": [("15:00", "22:30")]},
    "كرار": {"salary": 75000, "shifts": [("15:00", "22:30")]},
}

st.set_page_config(page_title="نظام بصمة 2026", layout="wide")

# واجهة الدخول
st.sidebar.title("🔐 تسجيل الدخول")
user_role = st.sidebar.radio("نوع الحساب:", ["موظف", "مدير"])

if user_role == "موظف":
    st.header("📲 لوحة الموظف")
    emp_name = st.selectbox("اختر اسمك:", list(EMPLOYEES.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 بصمة حضور"):
            st.success(f"تم تسجيل حضور {emp_name} في {datetime.now().strftime('%H:%M')}")
    with col2:
        if st.button("🔵 بصمة انصراف"):
            st.info("تم تسجيل الانصراف. سيتم حساب الأوفر تايم تلقائياً.")

    st.divider()
    st.subheader("📝 طلبات")
    with st.expander("تقديم طلب إجازة / سلفة"):
        request_type = st.selectbox("نوع الطلب:", ["إجازة", "سلفة"])
        reason = st.text_area("السبب:")
        if st.button("إرسال الطلب للمدير"):
            st.warning("تم الإرسال، بانتظار موافقة المدير لإلغاء الخصم.")

elif user_role == "مدير":
    st.header("👨‍💼 لوحة تحكم المدير")
    st.subheader("📊 ملخص رواتب الأسبوع")
    
    # عرض الرواتب (يوم الخميس فقط تظهر النتائج النهائية)
    is_thursday = datetime.now().weekday() == 3 # 3 يعني الخميس في بعض الأنظمة
    
    if st.button("🔄 تحديث وحساب الرواتب"):
        st.write("جاري معالجة البيانات بناءً على قوانين التأخير (5 دقائق)...")
        # هنا سنضع جدول البيانات لاحقاً