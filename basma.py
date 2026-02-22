import streamlit as st
from datetime import datetime
import requests
import pandas as pd

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

def clean_name(name):
    if pd.isna(name): return ""
    return str(name).strip().replace("أ", "ا").replace("إ", "ا")

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

def get_total_discounts(name):
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df['data'] = pd.to_datetime(df['data']).dt.date
        reset_entries = df[df['type'] == 'تصفية أسبوعية']
        if not reset_entries.empty:
            last_reset_date = reset_entries['data'].max()
        else:
            last_reset_date = datetime(2000, 1, 1).date()
        target_name = clean_name(name)
        mask = (df['name'].apply(clean_name) == target_name) & (df['data'] >= last_reset_date)
        return int(df.loc[mask, 'discount'].sum())
    except:
        return 0

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")

st.sidebar.title("🔐 بوابة الدخول")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        weekly_salary = STAFF_DATA[selected_name]['salary']
        total_discounts = get_total_discounts(selected_name)
        final_salary = weekly_salary - total_discounts
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الكلي", f"{weekly_salary:,} د.ع")
        col_m2.metric("خصومات الأسبوع", f"{total_discounts:,} د.ع")
        col_m3.metric("صافي الخميس", f"{final_salary:,} د.ع")
        
        st.divider()
        st.subheader("⏱️ تسجيل البصمة")
        now = datetime.now()
        c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            off_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            d1 = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            d2 = datetime.strptime(off_start, "%H:%M")
            diff = (d1 - d2).total_seconds() / 60
            discount = int(diff * 200) if diff > 5 else 0
            if discount > 0: st.error(f"تأخير {int(diff)} دقيقة. الخصم: {discount:,} د.ع")
            else: st.success("تم الحضور في الوقت!")
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            st.info(f"تم الانصراف: {c_time}")
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)

elif user_role == "المدير":
    admin_pass = st.sidebar.text_input("رمز المدير:", type="password")
    if admin_pass == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        # --- قسم الغياب ---
        st.subheader("🚫 تسجيل غياب")
        selected_absent = st.selectbox("اختر الموظف الغائب:", list(STAFF_DATA.keys()))
        if st.button(f"خصم غياب لـ {selected_absent} (-15,000)"):
            c_date, c_time = datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S")
            send_to_google(selected_absent, c_date, c_time, "غياب انقطاع", 15000, 0)
            st.error(f"تم تسجيل غياب لـ {selected_absent}")
            st.rerun()

        st.divider()
        
        # --- قسم ترتيب الرواتب الجديد ---
        st.subheader("🗓️ ترتيب رواتب يوم الخميس")
        if st.button("📊 عرض كشف الرواتب لهذا الأسبوع"):
            salary_list = []
            for name, data in STAFF_DATA.items():
                dis = get_total_discounts(name)
                net = data['salary'] - dis
                salary_list.append({
                    "الموظف": name,
                    "الراتب الكلي": f"{data['salary']:,}",
                    "مجموع الخصم": f"{dis:,}",
                    "الصافي النهائي": net
                })
            
            # إنشاء جدول (DataFrame) وترتيبه حسب الصافي
            df_salaries = pd.DataFrame(salary_list)
            df_salaries = df_salaries.sort_values(by="الصافي النهائي", ascending=False)
            
            # تجميل العرض للمدير
            df_salaries["الصافي النهائي"] = df_salaries["الصافي النهائي"].apply(lambda x: f"{x:,} د.ع")
            st.table(df_salaries)
            st.success("تم ترتيب الرواتب من الأعلى صافي إلى الأقل.")

        st.divider()
        if st.button("🔄 تصفير وبدء أسبوع جديد (للجميع)"):
            today = datetime.now().strftime("%Y-%m-%d")
            send_to_google("النظام", today, "00:00", "تصفية أسبوعية", 0, 0)
            st.balloons()
            st.success("تم تصفير العدادات للأسبوع الجديد.")
            st.rerun()
