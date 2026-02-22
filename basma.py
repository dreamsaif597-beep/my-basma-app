import streamlit as st
from datetime import datetime, timedelta

# 1. قاعدة بيانات الموظفين (الرواتب والأوقات)
STAFF_DATA = {
    "أمير": {"salary": 115000, "shifts": [("16:00", "23:00")], "type": "single"},
    "حارث": {"salary": 135000, "shifts": [("15:00", "22:00")], "type": "single"},
    "صادق": {"salary": 75000, "shifts": [("15:00", "22:30")], "type": "single"},
    "كرار": {"salary": 75000, "shifts": [("15:00", "22:30")], "type": "single"},
    "فؤاد": {"salary": 165000, "shifts": [("10:20", "15:00"), ("17:20", "22:00")], "type": "double"},
    "ياسر": {"salary": 115000, "shifts": [("10:00", "13:00"), ("15:00", "23:00")], "type": "double"}
}

st.set_page_config(page_title="نظام بصمة محل 2026", layout="centered")

# نظام الدخول
st.sidebar.title("🔐 تسجيل الدخول")
mode = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if mode == "موظف":
    name = st.sidebar.selectbox("اختر اسمك", list(STAFF_DATA.keys()))
    password = st.sidebar.text_input("كلمة المرور", type="password", help="سيتم حفظها تلقائياً في المتصفح")
    
    st.header(f"أهلاً {name}")
    
    # عرض ملخص الراتب للموظف فقط
    col1, col2, col3 = st.columns(3)
    col1.metric("الراتب الأسبوعي", f"{STAFF_DATA[name]['salary']:,} د.ع")
    col2.metric("إجمالي الخصم", "0 د.ع") # سيتحدث من قاعدة البيانات لاحقاً
    col3.metric("الصافي التقريبي", f"{STAFF_DATA[name]['salary']:,} د.ع")

    st.divider()
    
    # أزرار البصمة
    st.subheader("⏱️ تسجيل الوقت")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 بصمة حضور"):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            # منطق حساب التأخير (5 دقائق سماح)
            # سنربطها بجدول البيانات في الخطوة القادمة
            st.success(f"تم تسجيل الحضور: {current_time}")
            
    with c2:
        if st.button("🔵 بصمة انصراف"):
            st.info("تم تسجيل الانصراف وحساب الإضافي")

    # طلبات الإجازة والسلفة
    st.divider()
    with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
        req_type = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
        amount_reason = st.text_area("التفاصيل (السبب أو المبلغ)")
        if st.button("إرسال الطلب للمدير"):
            st.warning("تم إرسال الطلب، بانتظار موافقة المدير لإلغاء الخصم")

elif mode == "المدير":
    st.sidebar.warning("لوحة التحكم خاصة بالمدير فقط")
    admin_pass = st.sidebar.text_input("رمز المدير", type="password")
    
    if admin_pass == "2026": # يمكنك تغييره لاحقاً
        st.header("📊 لوحة تحكم المدير")
        
        # عرض طلبات الموظفين
        st.subheader("🔔 الإشعارات والطلبات")
        st.write("1. طلب إجازة من **أمير**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ موافقة (يلغى الخصم)"):
                st.success("تمت الموافقة وإلغاء خصم أمير")
        with col_b:
            if st.button("❌ رفض"):
                st.error("تم رفض الطلب")
        
        st.divider()
        st.subheader("💰 تصفية الخميس")
        if st.button("إتمام التصفية الأسبوعية"):
            st.balloons()
            st.info("تم ترحيل البيانات وتصفير السجلات للأسبوع الجديد")
    else:
        st.error("يرجى إدخال رمز المدير الصحيح")
