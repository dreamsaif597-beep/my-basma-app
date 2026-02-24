import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# --- تحميل البيانات الحساسة من متغيرات البيئة ---
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "5566")

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": os.getenv("AMIR_PASS", "1122"), "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": os.getenv("FUAD_PASS", "1133"), "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": os.getenv("HARITH_PASS", "1144"), "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": os.getenv("YASIR_PASS", "1155"), "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": os.getenv("SADIQ_PASS", "1166"), "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": os.getenv("KARRAR_PASS", "1177"), "start": "15:00", "end": "22:30", "type": "single"},
}

FORM_URL = os.getenv("FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse")
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

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
        response = requests.post(FORM_URL, data=payload, timeout=7)
        return response.status_code == 200
    except Exception as e: 
        st.error(f"فشل الاتصال بجوجل: {str(e)}")
        return False

@st.cache_data(ttl=5)
def fetch_and_clean_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        
        for col in ['name', 'type', 'data']:
            df[col] = df[col].fillna("").astype(str).str.strip()
            
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        
        # منطق التصفية الأسبوعية
        reset_indices = df[df['type'] == "تصفية أسبوعية"].index
        if not reset_indices.empty:
            last_reset = reset_indices.max()
            df = df.iloc[last_reset + 1:].reset_index(drop=True)
            
        return df
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return pd.DataFrame()

def calculate_delay_penalty(current_time_str, start_time_str):
    """حساب خصم التأخير"""
    try:
        t_now = datetime.strptime(current_time_str, "%H:%M")
        t_start = datetime.strptime(start_time_str, "%H:%M")
        
        if t_now > t_start:
            diff_min = (t_now - t_start).total_seconds() / 60
            if diff_min > 5:  # سماح 5 دقائق
                return int(diff_min * 200)
        return 0
    except:
        return 0

def calculate_overtime(current_time_str, end_time_str):
    """حساب الوقت الإضافي"""
    try:
        t_now = datetime.strptime(current_time_str, "%H:%M")
        t_end = datetime.strptime(end_time_str, "%H:%M")
        
        if t_now > t_end:
            diff_ov = (t_now - t_end).total_seconds() / 60
            if diff_ov > 1:
                return int(diff_ov * 100)
        return 0
    except:
        return 0

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
if 'auth' not in st.session_state: 
    st.session_state['auth'] = False
    st.session_state['last_activity'] = time.time()

# التحقق من انتهاء الجلسة
if st.session_state['auth']:
    if time.time() - st.session_state['last_activity'] > 1800:  # 30 دقيقة
        st.session_state['auth'] = False
        st.rerun()

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
                st.session_state.update({
                    'auth': True, 
                    'user': user_sel, 
                    'role': "موظف",
                    'last_activity': time.time()
                })
                if remember: 
                    st.session_state[pass_key] = user_pass
                st.success("تم تسجيل الدخول بنجاح!")
                time.sleep(1)
                st.rerun()
            else: 
                st.error("الرمز خطأ!")
                
    else:
        admin_pass = st.text_input("رمز المدير:", type="password")
        if st.button("دخول المدير"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.update({
                    'auth': True, 
                    'role': "المدير",
                    'last_activity': time.time()
                })
                st.success("مرحباً بك أيها المدير!")
                time.sleep(1)
                st.rerun()
            else: 
                st.error("الرمز خطأ!")
    
    st.info("ملاحظة: النظام سيتوقف بعد 30 دقيقة من عدم النشاط")
    st.stop()

# --- تحديث وقت النشاط ---
st.session_state['last_activity'] = time.time()

# --- القائمة الجانبية ---
with st.sidebar:
    st.write(f"👤 {st.session_state['role']}")
    if st.session_state['role'] == "موظف":
        st.write(f"👋 {st.session_state['user']}")
    
    if st.button("🚪 تسجيل خروج"):
        st.session_state.update({'auth': False})
        st.rerun()
    
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    st.header(f"👋 أهلاً {name}")
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].str.contains("طلب|مؤرشف", na=False))]
    
    salary = STAFF_DATA[name]['salary']
    total_disc = int(user_records['discount'].sum())
    total_ov = int(user_records['overtime'].sum())
    net_emp = salary - total_disc + total_ov

    col1, col2, col3 = st.columns(3)
    col1.metric("الراتب", f"{salary:,}")
    col2.metric("الخصومات", f"{total_disc:,}")
    col3.metric("الصافي", f"{net_emp:,}")

    st.divider()
    now = datetime.now()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
    current_time_short = now.strftime("%H:%M")

    btn1, btn2 = st.columns(2)
    
    # تسجيل الحضور
    if btn1.button("📥 تسجيل حضور", use_container_width=True):
        emp = STAFF_DATA[name]
        start_t_str = emp['start'] if emp['type'] == 'single' else emp['s1']
        
        disc = calculate_delay_penalty(current_time_short, start_t_str)
        
        if send_to_google(name, c_date, c_time, "حضور", disc, 0):
            st.cache_data.clear()
            st.success(f"✅ تم تسجيل الحضور {c_time}")
            if disc > 0:
                st.warning(f"⚠️ خصم تأخير: {disc:,} دينار")
            time.sleep(2)
            st.rerun()

    # تسجيل الانصراف
    if btn2.button("📤 تسجيل انصراف", use_container_width=True):
        emp = STAFF_DATA[name]
        end_t_str = emp['end'] if emp['type'] == 'single' else emp['e2']
        
        ov = calculate_overtime(current_time_short, end_t_str)
        
        if send_to_google(name, c_date, c_time, "انصراف", 0, ov):
            st.cache_data.clear()
            st.success(f"✅ تم تسجيل الانصراف {c_time}")
            if ov > 0:
                st.info(f"💰 وقت إضافي: {ov:,} دينار")
            time.sleep(2)
            st.rerun()

    # سجل الحركات
    with st.expander("📊 سجل الحركات (هذا الأسبوع)"):
        disp = user_records[user_records['type'] != "انصراف"].copy()
        if not disp.empty:
            disp = disp[['data', 'type', 'discount', 'overtime']]
            disp.columns = ["التاريخ", "النوع", "خصم", "مكافأة"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد سجلات لهذا الأسبوع")

    # طلبات الموظف
    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
        if t_req == "سلفة":
            amt_req = st.number_input("المبلغ (دينار)", min_value=0, step=5000, value=50000)
        else:
            amt_req = 0
        reason = st.text_input("السبب (اختياري)")
        
        if st.button("📨 إرسال الطلب"):
            req_time = f"{c_time} | {reason}" if reason else c_time
            if send_to_google(name, req_time, c_date, f"طلب {t_req}", amt_req, 0):
                st.success("✅ تم إرسال الطلب للمدير")
                time.sleep(2)
                st.rerun()

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.header("👑 لوحة المدير")
    
    if st.button("🔄 تحديث الكشوفات والطلبات"):
        st.cache_data.clear()
        st.success("تم تحديث البيانات")
        time.sleep(1)
        st.rerun()
        
    df_raw = fetch_and_clean_data()
    
    # قسم الطلبات المعلقة
    st.subheader("📩 الطلبات المعلقة")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived)]
        
        if not pending.empty:
            for i, row in pending[::-1].iterrows():
                with st.expander(f"📌 {row['name']} - {row['type']}"):
                    st.write(f"**التفاصيل:** {row['data']}")
                    if "سلفة" in row['type']:
                        st.write(f"**المبلغ:** {row['discount']:,} دينار")
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("✅ موافقة", key=f"y{i}", use_container_width=True):
                        if "سلفة" in row['type']:
                            send_to_google(row['name'], f"سلفة مقبولة: {row['data']}", "00:00", "سلفة مقبولة", row['discount'], 0)
                        send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                        st.cache_data.clear()
                        st.success("تمت الموافقة")
                        time.sleep(1)
                        st.rerun()
                    if c2.button("❌ رفض", key=f"n{i}", use_container_width=True):
                        send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                        st.cache_data.clear()
                        st.warning("تم الرفض")
                        time.sleep(1)
                        st.rerun()
                    if c3.button("⏸ تأجيل", key=f"p{i}", use_container_width=True):
                        st.info("تم تأجيل البت في الطلب")
        else: 
            st.info("🎉 لا توجد طلبات معلقة.")
    else:
        st.warning("لا توجد بيانات متاحة")

    st.divider()
    
    # قسم الإجراءات السريعة
    st.subheader("⚡ إجراءات سريعة")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ➕ مكافأة يدوية")
        e_ov = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="e_ov")
        a_ov = st.number_input("المبلغ (دينار):", step=1000, min_value=0)
        if st.button("💸 إضافة المكافأة", use_container_width=True):
            if send_to_google(e_ov, datetime.now().strftime("%Y-%m-%d"), "مكافأة يدوية", "مكافأة", 0, a_ov):
                st.cache_data.clear()
                st.success(f"تمت إضافة {a_ov:,} دينار مكافأة لـ {e_ov}")
                time.sleep(1)
                st.rerun()
    
    with col2:
        st.markdown("#### 🚫 تسجيل غياب")
        e_ab = st.selectbox("الموظف:", list(STAFF_DATA.keys()), key="e_ab")
        discount_amount = st.number_input("مبلغ الخصم (دينار):", value=15000, step=5000)
        if st.button("⚠️ خصم غياب", use_container_width=True):
            if send_to_google(e_ab, datetime.now().strftime("%Y-%m-%d"), "غياب", "غياب", discount_amount, 0):
                st.cache_data.clear()
                st.error(f"تم خصم {discount_amount:,} دينار من {e_ab} بسبب الغياب")
                time.sleep(1)
                st.rerun()

    st.divider()
    
    # قسم كشوف الرواتب
    if st.button("📊 عرض كشف الرواتب الحالي", use_container_width=True):
        st.subheader("📋 كشف الرواتب الشهري")
        
        active_df = fetch_and_clean_data()
        clean = active_df[~active_df['type'].str.contains("طلب|مؤرشف", na=False)]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        
        salary_data = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            net = info['salary'] - d + o
            salary_data.append({
                "الموظف": n,
                "الراتب الأساسي": f"{info['salary']:,}",
                "إجمالي الخصومات": f"{d:,}",
                "إجمالي المكافآت": f"{o:,}",
                "الصافي": f"{net:,}"
            })
        
        salary_df = pd.DataFrame(salary_data)
        st.dataframe(salary_df, use_container_width=True, hide_index=True)
        
        # مجموع عام
        total_salary = sum(info['salary'] for info in STAFF_DATA.values())
        total_discount = sum(int(totals.loc[n, 'discount']) if n in totals.index else 0 for n in STAFF_DATA.keys())
        total_overtime = sum(int(totals.loc[n, 'overtime']) if n in totals.index else 0 for n in STAFF_DATA.keys())
        total_net = total_salary - total_discount + total_overtime
        
        st.metric("إجمالي الرواتب", f"{total_salary:,}")
        st.metric("إجمالي الخصومات", f"{total_discount:,}")
        st.metric("إجمالي المكافآت", f"{total_overtime:,}")
        st.metric("إجمالي الصافي", f"{total_net:,}")

    st.divider()
    
    # قسم التصفية الأسبوعية
    st.subheader("🔄 إدارة النظام")
    if st.button("🗑️ تصفية بيانات الأسبوع", use_container_width=True):
        if send_to_google("المدير", datetime.now().strftime("%Y-%m-%d"), "تصفية أسبوعية", "تصفية أسبوعية", 0, 0):
            st.cache_data.clear()
            st.success("✅ تمت تصفية بيانات الأسبوع بنجاح")
            time.sleep(2)
            st.rerun()

# --- تذييل الصفحة ---
st.divider()
st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | نظام بصمة البسمة © 2024")
