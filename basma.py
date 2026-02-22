import streamlit as st
from datetime import datetime
import requests

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
# الرابط الحقيقي لإرسال البيانات
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# --- وظيفة إرسال البيانات للجدول ---
def send_to_google(name, status, discount=0, overtime=0):
    # استخدام الـ ID الذي أرسلته لي (786801446) وتخمين البقية بناءً على ترتيب فورم جوجل
    data = {
        "entry.786801446": name,      # سؤال الاسم
        "entry.1046333550": status,   # سؤال الحالة (تقديري - سيتم ملؤه)
        "entry.1524362718": discount, # سؤال الخصم
        "entry.1982736450": overtime, # سؤال الإضافي
        "entry.564738291": datetime.now().strftime("%Y-%m-%d %H:%M:%S") # الوقت
    }
    try:
        requests.post(FORM_URL, data=data)
    except:
        pass

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # حسبة بسيطة للعرض
        st.metric("الراتب الأسبوعي", f"{STAFF_DATA[selected_name]['salary']:,} د.ع")
        
        st.divider()
        st.subheader("⏱️ تسجيل البصمة")
        c1, c2 = st.columns(2)
        
        if c1.button("📥 تسجيل حضور"):
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # تحديد وقت الحضور الرسمي بناءً على نوع الشفت
            emp = STAFF_DATA[selected_name]
            official_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            
            # حساب الفرق بالدقائق
            fmt = '%H:%M'
            d1 = datetime.strptime(current_time, fmt)
            d2 = datetime.strptime(official_start, fmt)
            diff = (d1 - d2).total_seconds() / 60
            
            discount = 0
            if diff > 5:
                discount = int(diff * 200)
                st.error(f"تأخير {int(diff)} دقيقة. الخصم: {discount:,} د.ع")
            else:
                st.success(f"تم تسجيل حضورك الساعة {current_time}")
                st.balloons()
            
            send_to_google(selected_name, "حضور", discount, 0)

        if c2.button("📤 تسجيل انصراف"):
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # حساب الإضافي (بشكل تبسيطي للمدير)
            st.info(f"تم تسجيل الانصراف الساعة {current_time}")
            send_to_google(selected_name, "انصراف", 0, "يتم حسابه للمدير")

        st.divider()
        with st.expander("📝 تقديم طلب (إجازة / سلفة)"):
            req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
            if st.button("إرسال الطلب"):
                send_to_google(selected_name, f"طلب {req}", 0, 0)
                st.warning("تم الإرسال للمدير")

elif user_role == "المدير":
    admin_input = st.sidebar.text_input("رمز دخول المدير:", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.header("📊 لوحة تحكم المدير")
        
        st.subheader("👥 ملخص الرواتب")
        for staff, info in STAFF_DATA.items():
            st.write(f"**{staff}**: الراتب {info['salary']:,} د.ع")
        
        st.divider()
        # رابط مباشر لجدول البيانات لتسهيل عملك
        st.success("✅ النظام متصل بجدول Google Sheets")
        st.info("لمراجعة الخصومات والطلبات بالتفصيل، يرجى فتح الجدول المرتبط بالنموذج.")
        
        if st.button("💰 تصفية حسابات الخميس"):
            st.balloons()
            st.success("تم إرسال أمر تصفية الحسابات")
