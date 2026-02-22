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
        "entry.1254543219": int(discount), 
        "entry.1151470082": int(overtime)  
    }
    try: requests.post(FORM_URL, data=payload, timeout=5)
    except: pass

@st.cache_data(ttl=5)
def fetch_and_clean_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&cache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        df['name'] = df['name'].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0)
        
        resets = df[df['type'] == 'تصفية أسبوعية']
        if not resets.empty:
            last_reset_idx = resets.index[-1]
            active_df = df.iloc[last_reset_idx + 1:].copy()
        else:
            active_df = df.copy()
            
        active_df = active_df[~active_df['type'].str.contains("طلب|مؤرشف", na=False)]
        return active_df
    except:
        return pd.DataFrame()

def get_active_financials(name):
    df = fetch_and_clean_data()
    if df.empty: return {"discounts": 0, "overtime": 0}
    user_data = df[df['name'] == name]
    return {
        "discounts": int(user_data['discount'].sum()),
        "overtime": int(user_data['overtime'].sum())
    }

# --- واجهة التطبيق ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        fin = get_active_financials(selected_name)
        weekly_salary = STAFF_DATA[selected_name]['salary']
        net_salary = weekly_salary - fin['discounts'] + fin['overtime']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,}")
        col_m2.metric("إجمالي الخصم", f"{fin['discounts']:,}")
        col_m3.metric("الصافي الحالي", f"{net_salary:,}")
        
        st.divider()
        now = datetime.now()
        c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

        c1, c2 = st.columns(2)
        if c1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[selected_name]
            off_start = emp['start'] if emp['type'] == 'single' else emp['s1']
            diff = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(off_start, "%H:%M")).total_seconds() / 60
            discount = int(diff * 200) if diff > 5 else 0
            send_to_google(selected_name, c_date, c_time, "حضور", discount, 0)
            st.success(f"تم التسجيل. الخصم: {discount:,}"); time.sleep(1); st.cache_data.clear(); st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            emp = STAFF_DATA[selected_name]
            off_end = emp['end'] if emp['type'] == 'single' else emp['e2']
            time_now = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
            time_end = datetime.strptime(off_end, "%H:%M")
            diff_ov = (time_now - time_end).total_seconds() / 60
            ov_amt = int(diff_ov * 100) if diff_ov > 1 else 0
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, ov_amt)
            st.info(f"تم الانصراف. الإضافي: {ov_amt:,}"); time.sleep(1); st.cache_data.clear(); st.rerun()

        st.divider()
        with st.expander("📝 طلب إجازة أو سلفة"):
            t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
            val_req = st.number_input("المبلغ", min_value=0, step=5000)
            reason = st.text_input("السبب")
            if st.button("إرسال الطلب"):
                u_id = f"{reason} ({now.strftime('%H:%M:%S')})"
                send_to_google(selected_name, u_id, c_date, f"طلب {t_req}", val_req, 0)
                st.warning("تم الإرسال للمدير")

elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")

        st.subheader("📩 طلبات معلقة")
        try:
            df_raw = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
            df_raw.columns = [c.strip() for c in df_raw.columns]
            reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
            archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
            pending = reqs[~reqs['data'].isin(archived)]

            if not pending.empty:
                for idx, row in pending[::-1].iterrows():
                    with st.expander(f"📌 {row['type']} - {row['name']}"):
                        st.write(f"**التفاصيل:** {row['data']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"ok_{idx}"):
                            if "سلفة" in str(row['type']):
                                send_to_google(row['name'], f"موافقة سلفة: {row['data']}", "00:00", "سلفة مقبولة", row['discount'], 0)
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.success("تم"); time.sleep(1); st.rerun()
                        if c2.button("❌ رفض", key=f"no_{idx}"):
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.error("تم الرفض"); time.sleep(1); st.rerun()
            else:
                st.info("لا توجد طلبات.")
        except: pass

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("➕ أوفر تايم")
            emp_ov = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="ov")
            amt_ov = st.number_input("المبلغ:", min_value=0, step=1000)
            if st.button("إضافة المكافأة"):
                send_to_google(emp_ov, datetime.now().strftime("%Y-%m-%d"), "مكافأة", "أوفر تايم", 0, amt_ov)
                st.success("تمت الإضافة"); time.sleep(1); st.cache_data.clear(); st.rerun()
        
        with col_b:
            st.subheader("🚫 غياب")
            emp_ab = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="ab")
            if st.button("خصم غياب (15,000)"):
                send_to_google(emp_ab, datetime.now().strftime("%Y-%m-%d"), "غياب", "غياب", 15000, 0)
                st.error("تم الخصم"); time.sleep(1); st.cache_data.clear(); st.rerun()

        st.divider()
        if st.button("📊 عرض كشف الرواتب"):
            active_df = fetch_and_clean_data()
            if not active_df.empty:
                totals = active_df.groupby('name')[['discount', 'overtime']].sum()
                summary = []
                for name, info in STAFF_DATA.items():
                    disc = int(totals.loc[name, 'discount']) if name in totals.index else 0
                    over = int(totals.loc[name, 'overtime']) if name in totals.index else 0
                    summary.append({
                        "الموظف": name, "الراتب": info['salary'], 
                        "الخصم": disc, "الإضافي": over, 
                        "الصافي": info['salary'] - disc + over
                    })
                st.table(pd.DataFrame(summary).sort_values(by="الصافي", ascending=False))
            else:
                st.warning("لا توجد بيانات مسجلة حالياً.")

        st.divider()
        if st.button("🔄 تصفير الأسبوع"):
            send_to_google("نظام_تصفير", datetime.now().strftime("%Y-%m-%d"), "00:00", "تصفية أسبوعية", 0, 0)
            st.cache_data.clear()
            st.balloons(); time.sleep(1); st.rerun()
