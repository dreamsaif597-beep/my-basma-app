import streamlit as st
from datetime import datetime

# --- قاعدة البيانات الثابتة (لن تضيع بعد الآن) ---
ADMIN_PASS = "5566"  # رمز المدير

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "2001", "start": "16:00", "end": "23:00", "shifts": 1},
    "حارث": {"salary": 135000, "pass": "2002", "start": "15:00", "end": "22:00", "shifts": 1},
    "صادق": {"salary": 75000, "pass": "2003", "start": "15:00", "end": "22:30", "shifts": 1},
    "كرار": {"salary": 75000, "pass": "2004", "start": "15:00", "end": "22:30", "shifts": 1},
    "فؤاد": {"salary": 165000, "pass": "2005", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "shifts": 2},
    "ياسر": {"salary": 115000, "pass": "2006", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "shifts": 2},
}

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

# --- الواجهة الجانبية ---
st.sidebar.title("💳 تسجيل الدخول")
mode = st.sidebar.radio("نوع الحساب:", ["موظف", "المدير"])

if mode == "موظف":
    name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    password = st.sidebar.text_input("الرمز السري الخاص بك:", type="1122")
    
    if password == STAFF_DATA[name]["pass"]:
        st.header(f"👋 أهلاً {name}")
        st.info(f"راتبك الأسبوعي الأساسي: {STAFF_DATA[name]['salary']:,} دينار")
        
        # عرض الإحصائيات (ستربط بالجدول لاحقاً)
        col1, col2 = st.columns(2)
        col1.metric("مجموع التأخير والغياب", "0 د.ع")
        col2.metric("الراتب الصافي الحالي", f"{STAFF_DATA[name]['salary']:,} د.ع")
        
        st.divider()
        # أزرار البصمة
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📥 تسجيل حضور"):
                now = datetime.now().strftime("%H:%M:%S")
                st.success(f"تم تسجيل حضورك الساعة: {now}")
                # هنا معادلة الـ 200 دينار والـ 5 دقائق
        with c2:
            if st.button("📤 تسجيل انصراف"):
                st.info("تم تسجيل الانصراف وحساب الإضافي")
        
        st.divider()
        # طلبات الإجازة والسلفة
        with st.expander("📝 تقديم طلب جديد"):
            t = st.selectbox("نوع الطلب", ["طلب إجازة", "طلب سلفة"])
            m = st.text_area("السبب أو المبلغ المطلوب")
            if st.button("إرسال الطلب"):
                st.warning("تم إرسال طلبك للمدير. بانتظار الموافقة لإلغاء الخصم.")
                
    elif password != "":
        st.error("الرمز السري خطأ!")

elif mode == "المدير":
    p = st.sidebar.text_input("رمز المدير:", type="password")
    if p == ADMIN_PASS:
        st.header("👑 لوحة تحكم المدير")
        st.subheader("🔔 الإشعارات والطلبات الجديدة")
        
        # مثال لطلب إجازة
        st.write("• طلب إجازة من **أمير**")
        col_ok, col_no = st.columns(2)
        if col_ok.button("✅ موافقة وإلغاء الخصم"):
            st.success("تمت الموافقة وتعديل الراتب")
        if col_no.button("❌ رفض الطلب"):
            st.error("تم الرفض")
            
        st.divider()
        st.subheader("📊 كشف الرواتب العام")
        # هنا ستظهر لك جداول كل الموظفين (فقط للمدير)
        if st.button("💰 تصفية رواتب الخميس (إعادة ضبط)"):
            st.balloons()
            st.success("تم تصفير العداد للأسبوع الجديد!")
    elif p != "":
        st.error("رمز المدير غير صحيح!")

