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

# --- الوظائف المساعدة ---
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

def get_active_df():
    try:
        # جلب البيانات الخام
        df = pd.read_csv(f"{SHEET_CSV_URL}&cache={time.time()}")
        
        # إجبار البرنامج على تسمية الأعمدة الـ 7 الأولى (لحل مشكلة KeyError)
        # الترتيب: Timestamp, الاسم, التاريخ, الملاحظات, النوع, الخصم, الإضافي
        new_columns = ['timestamp', 'name', 'date', 'data', 'type', 'discount', 'overtime']
        df.columns = new_columns[:len(df.columns)] 
        
        # تنظيف البيانات
        df['name'] = df['name'].fillna("").astype(str).str.strip()
        df['type'] = df['type'].fillna("").astype(str).str.strip()
        
        # تحديد آخر تصفير
        resets = df[df['type'] == 'تصفية أسبوعية'].index
        return df.iloc[resets.max() + 1:] if not resets.empty else df
    except Exception as e:
        return pd.DataFrame()

# --- واجهة التطبيق ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        active_df = get_active_df()
        user_df = active_df[active_df['name'] == selected_name]
        
        # تحويل القيم لأرقام لضمان الجمع الصحيح
        disc_total = pd.to_numeric(user_df['discount'], errors='coerce').sum() if not user_df.empty else 0
        over_total = pd.to_numeric(user_df['overtime'], errors='coerce').sum() if not user_df.empty else 0
        
        weekly_salary = STAFF_DATA[selected_name]['salary']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,}")
        col_m2.metric("إجمالي الخصم", f"{int(disc_total):,}")
        col_m3.metric("الصافي الحالي", f"{int(weekly_salary - disc_total + over_total):,}")
        
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
            st.success(f"تم الحضور. الخصم: {discount:,}"); time.sleep(1); st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)
            st.info("تم الانصراف بنجاح")

        st.divider()
        with st.expander("📝 طلب إجازة أو سلفة"):
            t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
            val_req = st.number_input("المبلغ (للسلفة فقط)", min_value=0, step=5000)
            reason = st.text_input("السبب")
            if st.button("إرسال الطلب"):
                send_to_google(selected_name, c_date, reason, f"طلب {t_req}", val_req, 0)
                st.warning("تم إرسال الطلب للمدير")

elif user_role == "المدير":
    entered_admin_pass = st.sidebar.text_input("رمز المدير:", type="password")
    if entered_admin_pass == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        active_df = get_active_df()
        
        # 1. إدارة الطلبات
        st.subheader("📩 طلبات الموظفين المعلقة")
        if not active_df.empty and 'type' in active_df.columns:
            pending = active_df[active_df['type'].str.contains("طلب", na=False)]
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.expander(f"طلب من {row['name']} - {row['type']}"):
                        st.write(f"السبب/الملاحظات: {row['data']}")
                        if "سلفة" in row['type']: st.write(f"المبلغ: {row['discount']:,}")
                        
                        c_ok, c_no = st.columns(2)
                        if c_ok.button("✅ موافقة", key=f"ok_{idx}"):
                            label = "سلفة مقبولة" if "سلفة" in row['type'] else "إجازة مقبولة"
                            send_to_google(row['name'], "موافقة", "00:00", label, row['discount'], 0)
                            st.success("تمت الموافقة"); time.sleep(1); st.rerun()
                        
                        if c_no.button("❌ رفض", key=f"no_{idx}"):
                            disc = 15000 if "إجازة" in row['type'] else 0
                            send_to_google(row['name'], "مرفوض", "00:00", "طلب مرفوض", disc, 0)
                            st.error("تم الرفض والخصم"); time.sleep(1); st.rerun()
            else:
                st.write("لا توجد طلبات جديدة.")
        else:
            st.write("الجدول فارغ حالياً.")

        st.divider()
        # 2. كشف الرواتب
        if st.button("📊 عرض كشف الرواتب المُرتب"):
            summary = []
            for name, info in STAFF_DATA.items():
                u_df = active_df[active_df['name'] == name] if not active_df.empty else pd.DataFrame()
                d = int(pd.to_numeric(u_df['discount'], errors='coerce').sum() or 0)
                o = int(pd.to_numeric(u_df['overtime'], errors='coerce').sum() or 0)
                summary.append({"الموظف": name, "الراتب": info['salary
