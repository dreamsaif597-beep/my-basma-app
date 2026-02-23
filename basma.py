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
    try: 
        requests.post(FORM_URL, data=payload, timeout=7)
    except: 
        st.error("فشل الاتصال بجوجل، حاول مرة أخرى")

@st.cache_data(ttl=5) # زدنا الوقت شوي للاستقرار
def fetch_and_clean_data():
    try:
        # قراءة البيانات مع كسر الكاش لضمان أحدث البيانات
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        
        # تنظيف البيانات من الفراغات
        for col in ['name', 'type', 'data']:
            df[col] = df[col].fillna("").astype(str).str.strip()
            
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        
        # --- منطق التصفير الأسبوعي ---
        # نبحث عن آخر سطر فيه "تصفية أسبوعية"
        reset_indices = df[df['type'] == "تصفية أسبوعية"].index
        if not reset_indices.empty:
            last_reset = reset_indices.max()
            df = df.iloc[last_reset + 1:].reset_index(drop=True)
            
        return df
    except Exception as e:
        return pd.DataFrame()

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- واجهة تسجيل الدخول ---
if not st.session_state['auth']:
    st.title("🔐 تسجيل الدخول")
    role = st.radio("الدخول كـ:", ["موظف", "المدير"], horizontal=True)
    if role == "موظف":
        user_sel = st.selectbox("اسم الموظف:", list(STAFF_DATA.keys()))
        pass_key = f"saved_pass_{user_sel}"
        default_pass = st.session_state.get(pass_key, "")
        user_pass = st.text_input("الرمز السري:", value=default_pass, type="password")
        remember = st.checkbox("تذكر كلمة السر ✅", value=True if default_pass else False)
        if st.button("دخول الموظف"):
            if user_pass == STAFF_DATA[user_sel]["pass"]:
                st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
                if remember: st.session_state[pass_key] = user_pass
                st.rerun()
            else: st.error("الرمز خطأ!")
    else:
        admin_pass = st.text_input("رمز المدير:", type="password")
        if st.button("دخول المدير"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.update({'auth':True, 'role':"المدير"})
                st.rerun()
            else: st.error("الرمز خطأ!")
    st.stop()

# --- خروج ---
st.sidebar.button("🚪 تسجيل خروج", on_click=lambda: st.session_state.update({'auth': False}))

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    st.header(f"👋 أهلاً {name}")
    
    # جلب البيانات المنظفة (بعد آخر تصفية)
    df = fetch_and_clean_data()
    
    # تصفية سجلات هذا الموظف فقط (بعيداً عن الطلبات)
    user_records = df[(df['name'] == name) & (~df['type'].str.contains("طلب|مؤرشف", na=False))]
    
    salary = STAFF_DATA[name]['salary']
    total_disc = int(user_records['discount'].sum())
    total_ov = int(user_records['overtime'].sum())
    net_emp = salary - total_disc + total_ov

    col1, col2, col3 = st.columns(3)
    col1.metric("الراتب", f"{salary:,}")
    col2.metric("الخصومات", f"{total_disc:,}")
    col3.metric("الصافي", f"{net_emp:,}")

    with st.expander("📊 سجل الحركات (هذا الأسبوع)"):
        # استبعاد سجلات "انصراف" من الجدول لعرض المكافآت والخصومات فقط
        disp = user_records[user_records['type'] != "انصراف"].copy()
        if not disp.empty:
            disp = disp[['data', 'type', 'discount', 'overtime']]
            disp.columns = ["التاريخ", "النوع", "خصم", "مكافأة"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد حركات مالية (خصم أو مكافأة) سجلت لك هذا الأسبوع.")

    st.divider()
    now = datetime.now()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    btn1, btn2 = st.columns(2)
    if btn1.button("📥 تسجيل حضور"):
        emp = STAFF_DATA[name]
        start_t = emp['start'] if emp['type'] == 'single' else emp['s1']
        diff = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(start_t, "%H:%M")).total_seconds() / 60
        disc = int(diff * 200) if diff > 5 else 0
        send_to_google(name, c_date, c_time, "حضور", disc, 0)
        st.cache_data.clear()
        st.success(f"تم تسجيل الحضور. الخصم: {disc}"); time.sleep(1); st.rerun()

    if btn2.button("📤 تسجيل انصراف"):
        emp = STAFF_DATA[name]
        end_t = emp['end'] if emp['type'] == 'single' else emp['e2']
        diff_ov = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(end_t, "%H:%M")).total_seconds() / 60
        ov = int(diff_ov * 100) if diff_ov > 1 else 0
        send_to_google(name, c_date, c_time, "انصراف", 0, ov)
        st.cache_data.clear()
        st.info("تم تسجيل الانصراف"); time.sleep(1); st.rerun()

    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ (للسلف)", min_value=0, step=5000)
        reason = st.text_input("السبب")
        if st.button("إرسال الطلب"):
            send_to_google(name, f"{reason} | {c_time}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("تم إرسال الطلب")

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.header("👑 لوحة المدير")
    df_raw = fetch_and_clean_data()
    
    st.subheader("📩 الطلبات المعلقة")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived)]
        
        if not pending.empty:
            for i, row in pending[::-1].iterrows():
                with st.expander(f"📌 {row['name']} - {row['type']}"):
                    st.write(f"التفاصيل: {row['data']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ موافقة", key=f"y{i}"):
                        if "سلفة" in row['type']:
                            send_to_google(row['name'], f"سلفة مقبولة: {row['data']}", "00:00", "سلفة مقبولة", row['discount'], 0)
                        send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()
                    if c2.button("❌ رفض", key=f"n{i}"):
                        send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()
        else: st.info("لا توجد طلبات معلقة.")

    st.divider()
    cx, cy = st.columns(2)
    with cx:
        st.subheader("➕ مكافأة يدوية")
        e_ov = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="e_ov")
        a_ov = st.number_input("المبلغ:", step=1000)
        if st.button("إضافة المكافأة"):
            send_to_google(e_ov, datetime.now().strftime("%Y-%m-%d"), "مكافأة يدوية", "مكافأة", 0, a_ov)
            st.cache_data.clear(); st.success("تمت"); time.sleep(1); st.rerun()
    with cy:
        st.subheader("🚫 تسجيل غياب")
        e_ab = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="e_ab")
        if st.button("خصم 15,000 غياب"):
            send_to_google(e_ab, datetime.now().strftime("%Y-%m-%d"), "غياب", "غياب", 15000, 0)
            st.cache_data.clear(); st.error("تم الخصم"); time.sleep(1); st.rerun()

    st.divider()
    if st.button("📊 عرض كشف الرواتب (الحالي)"):
        active_df = fetch_and_clean_data()
        clean = active_df[~active_df['type'].str.contains("طلب|مؤرشف", na=False)]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        sum_list = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            sum_list.append({"الموظف": n, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(sum_list))

    st.divider()
    st.warning("⚠️ زر التصفير يمسح كل الحسابات والطلبات السابقة")
    if st.button("🔄 تصفير الأسبوع بالكامل"):
        send_to_google("نظام", "تصفير شامل", "00:00", "تصفية أسبوعية", 0, 0)
        st.cache_data.clear()
        st.balloons()
        st.success("تم التصفير بنجاح")
        time.sleep(2)
        st.rerun()
