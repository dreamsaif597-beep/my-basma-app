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
        df = pd.read_csv(f"{SHEET_CSV_URL}&cache={time.time()}")
        # ضمان أسماء الأعمدة بغض النظر عن لغة الشيت
        df.columns = ['Timestamp', 'name', 'date', 'data', 'type', 'discount', 'overtime']
        df['name'] = df['name'].str.strip()
        resets = df[df['type'] == 'تصفية أسبوعية'].index
        return df.iloc[resets.max() + 1:] if not resets.empty else df
    except:
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
        
        disc_total = int(user_df['discount'].sum()) if not user_df.empty else 0
        over_total = int(user_df['overtime'].sum()) if not user_df.empty else 0
        weekly_salary = STAFF_DATA[selected_name]['salary']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,}")
        col_m2.metric("إجمالي الخصم", f"{disc_total:,}")
        col_m3.metric("الصافي الحالي", f"{weekly_salary - disc_total + over_total:,}")
        
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
            st.success(f"تم الحضور. الخصم: {discount:,}"); time.sleep(2); st.rerun()

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
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        # 1. قسم إدارة الطلبات (الجدول اللي رجعناه)
        st.subheader("📩 طلبات الموظفين المعلقة")
        active_df = get_active_df()
        pending = active_df[active_df['type'].str.contains("طلب", na=False)]
        
        if not pending.empty:
            for idx, row in pending.iterrows():
                with st.expander(f"طلب من {row['name']} - {row['type']}"):
                    st.write(f"السبب: {row['data']}")
                    if "سلفة" in row['type']: st.write(f"المبلغ المطلوب: {row['discount']:,}")
                    
                    c_ok, c_no = st.columns(2)
                    if c_ok.button("✅ موافقة", key=f"ok_{idx}"):
                        # إذا سلفة ينزل المبلغ كخصم، إذا إجازة ينزل صفر
                        label = "سلفة مقبولة" if "سلفة" in row['type'] else "إجازة مقبولة"
                        send_to_google(row['name'], "موافقة", "00:00", label, row['discount'], 0)
                        st.success("تمت الموافقة"); time.sleep(1); st.rerun()
                    
                    if c_no.button("❌ رفض", key=f"no_{idx}"):
                        # إذا رفض إجازة يخصم 15000
                        disc = 15000 if "إجازة" in row['type'] else 0
                        send_to_google(row['name'], "مرفوض", "00:00", "طلب مرفوض", disc, 0)
                        st.error("تم الرفض والخصم"); time.sleep(1); st.rerun()
        else:
            st.write("لا توجد طلبات معلقة حالياً.")

        st.divider()
        # 2. إضافة يدوي (أوفر تايم / غياب)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("➕ إضافة أوفر تايم")
            emp_ov = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="ov")
            amt_ov = st.number_input("المبلغ:", min_value=0, step=1000)
            if st.button("إضافة المكافأة"):
                send_to_google(emp_ov, "مدير", "00:00", "أوفر تايم", 0, amt_ov)
                st.success("تمت الإضافة"); time.sleep(1); st.rerun()
        
        with col_b:
            st.subheader("🚫 تسجيل غياب مباشر")
            emp_ab = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="ab")
            if st.button("خصم غياب (15,000)"):
                send_to_google(emp_ab, "مدير", "00:00", "غياب", 15000, 0)
                st.error("تم الخصم"); time.sleep(1); st.rerun()

        st.divider()
        # 3. كشف الرواتب
        if st.button("📊 عرض كشف الرواتب المُرتب"):
            active_df = get_active_df()
            summary = []
            for name, info in STAFF_DATA.items():
                u_df = active_df[active_df['name'] == name]
                disc = int(u_df['discount'].sum()) if not u_df.empty else 0
                over = int(u_df['overtime'].sum()) if not u_df.empty else 0
                summary.append({"الموظف": name, "الراتب": info['salary'], "الخصم": disc, "الإضافي": over, "الصافي": info['salary'] - disc + over})
            st.table(pd.DataFrame(summary).sort_values(by="الصافي", ascending=False))

        st.divider()
        if st.button("🔄 تصفير الأسبوع"):
            send_to_google("نظام_تصفير", "تصفية", "00:00", "تصفية أسبوعية", 0, 0)
            st.balloons(); st.success("تم التصفير"); time.sleep(1); st.rerun()
