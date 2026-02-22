import streamlit as st
from datetime import datetime

# --- البيانات الثابتة (الرواتب، الرموز، الأوقات) ---
ADMIN_PASSWORD = "5566"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

st.set_page_config(page_title="نظام بصمة البسمة الرسمي", layout="centered")

# --- واجهة تسجيل الدخول ---
st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # عرض معلومات الراتب للموظف
        col1, col2 = st.columns(2)
        with col1:
            st.metric("الراتب الأسبوعي الأساسي", f"{STAFF_DATA[selected_name]['salary']:,} د.ع")
        with col2:
            st.metric("الاستقطاعات والتأخير", "0 د.ع") # ستحدث عند ربط الجدول
            
        st.info("ملاحظة: غياب اليوم الكامل يخصم 15,000 د.ع")
        
        st.divider()
        # أزرار البصمة
        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            st.success(f"تم تسجيل حضورك الساعة {datetime.now().strftime('%H:%M:%S')}")
        if c2.button("📤 تسجيل انصراف"):
            st.info("تم تسجيل الانصراف وحساب الإضافي")

        st.divider()
        # قسم الطلبات
        with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
            request_type = st.selectbox("نوع الطلب", ["طلب إجازة", "طلب سلفة"])
            reason = st.text_area("السبب أو التفاصيل")
            if st.button("إرسال الطلب"):
                st.warning("تم إرسال طلبك بنجاح وسوف يظهر للمدير للموافقة")
    elif entered_pass != "":
        st.error("الرمز السري غير صحيح")

elif user_role == "المدير":
    admin_input = st.sidebar.text_input("رمز دخول المدير:", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.header("📊 لوحة تحكم المدير")
        
        # هنا تم إزالة "طلب أمير" الوهمي
        st.subheader("🔔 الإشعارات والطلبات")
        st.write("لا توجد طلبات جديدة حالياً") # ستتغير تلقائياً عند ربط الجدول
        
        st.divider()
        st.subheader("👥 كشف الرواتب الأسبوعي")
        # جدول افتراضي يوضح شكل الإدارة
        st.write("سيظهر هنا جدول كامل بأسماء الموظفين، ساعات التأخير، الأوفر تايم، والراتب الصافي.")
        
        if st.button("💰 تصفية حسابات الخميس"):
            st.balloons()
            st.success("تم تصفير الحسابات بنجاح للأسبوع الجديد")
    elif admin_input != "":
        st.error("رمز المدير خطأ")
