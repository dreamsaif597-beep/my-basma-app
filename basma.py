import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import time

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

# --- وظيفة الإرسال (دون تغيير) ---
def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": discount, 
        "entry.1151470082": overtime  
    }
    try: requests.post(FORM_URL, data=payload, timeout=5)
    except: pass

# --- دالة جلب البيانات المنقحة (الحل الأكيد للوكفة) ---
def get_clean_data():
    try:
        # إضافة طابع زمني لمنع الكاش
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        
        # التأكد من وجود 7 أعمدة وتسميتها يدوياً
        if len(df.columns) >= 7:
            df = df.iloc[:, :7] # نأخذ أول 7 أعمدة فقط
            df.columns = ['ts', 'name', 'date', 'data', 'type', 'discount', 'overtime']
        
        # تنظيف البيانات من النل والفراغات
        df['name'] = df['name'].fillna("").astype(str).str.strip()
        df['type'] = df['type'].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0)
        
        # فلترة البيانات بعد آخر تصفير
        resets = df[df['type'].str.contains('تصفية', na=False)].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:]
        return df
    except Exception as e:
        st.sidebar.error(f"خطأ في الاتصال: {e}")
        return pd.DataFrame(columns=['ts', 'name', 'date', 'data', 'type', 'discount', 'overtime'])

# --- الواجهة ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        
        # حساب الحسابات الحالية
        df = get_clean_data()
        user_df = df[df['name'] == selected_name]
        d_total = int(user_df['discount'].sum())
        o_total = int(user_df['overtime'].sum())
        
        weekly_salary = STAFF_DATA[selected_name]['salary']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,}")
        col_m2.metric("إجمالي الخصم", f"{d_total:,}")
        col_m3.metric("الصافي الحالي", f"{weekly_salary - d_total + o_total:,}")
        
        st.divider()
        now = datetime.now()
        c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            official_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            diff = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(official_start, "%H:%M")).total_seconds() / 60
            discount = int(diff * 200) if diff > 5 else 0
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.success(f"تم الحضور. الخصم: {discount:,}"); time.sleep(1.5); st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)
            st.info("تم الانصراف")

        st.divider()
        with st.expander("📝 طلب سلفة / إجازة"):
            t = st.selectbox("النوع", ["إجازة", "سلفة"])
            v = st.number_input("المبلغ للسلفة", min_value=0, step=5000)
            r = st.text_input("السبب")
            if st.button("إرسال"):
                send_to_google(selected_name, c_date, r, f"طلب {t}", v, 0)
                st.toast("تم الإرسال")

elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة المدير")
        
        df = get_clean_data()
        
        # عرض الطلبات المعلقة
        st.subheader("📩 الطلبات")
        pending = df[df['type'].str.contains("طلب", na=False)]
        if not pending.empty:
            for idx, row in pending.iterrows():
                with st.expander(f"طلب من {row['name']}"):
                    st.write(f"النوع: {row['type']} | السبب: {row['data']}")
                    if st.button("✅ موافقة", key=f"y{idx}"):
                        send_to_google(row['name'], "مقبول", "00:00", "موافقة", row['discount'], 0)
                        st.rerun()
        else: st.write("لا توجد طلبات.")

        st.divider()
        # عرض الكشف المرتب
        if st.button("📊 تحديث وعرض الكشف العام"):
            summary = []
            for name, info in STAFF_DATA.items():
                u_df = df[df['name'] == name]
                d = int(u_df['discount'].sum())
                o = int(u_df['overtime'].sum())
                summary.append({"الموظف": name, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
            st.table(pd.DataFrame(summary).sort_values(by="الصافي", ascending=False))

        st.divider()
        if st.button("🔄 تصفير الأسبوع"):
            send_to_google("نظام_تصفير", "تصفية", "00:00", "تصفية أسبوعية", 0, 0)
            st.success("تم التصفير"); time.sleep(1); st.rerun()
