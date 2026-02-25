import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# حفظ بيانات الموظفين في الـ session_state
if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
        "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
    }

STAFF_DATA = st.session_state['staff_registry']

def get_iraq_time():
    return datetime.utcnow() + timedelta(hours=3)

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0):
    payload = {
        "entry.104291709": name,      
        "entry.786801446": data_val,  
        "entry.2093200411": time_val, 
        "entry.1043553703": type_val, 
        "entry.1254543219": int(discount), 
        "entry.1151470082": int(overtime)  
    }
    try: requests.post(FORM_URL, data=payload, timeout=7)
    except: st.error("فشل الاتصال بجوجل")

@st.cache_data(ttl=2)
def fetch_and_clean_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        for col in ['name', 'type', 'data']:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        
        resets = df[df['type'] == "تصفية أسبوعية"].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:].reset_index(drop=True)
        return df
    except: return pd.DataFrame()

# --- واجهة البرنامج ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 تسجيل الدخول")
    role = st.radio("الدخول كـ:", ["موظف", "المدير"], horizontal=True)
    if role == "موظف":
        user_sel = st.selectbox("اسم الموظف:", list(STAFF_DATA.keys()))
        user_pass = st.text_input("الرمز السري:", type="password")
        if st.button("دخول الموظف"):
            if user_pass == STAFF_DATA[user_sel]["pass"]:
                st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
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

st.sidebar.button("🚪 خروج", on_click=lambda: st.session_state.update({'auth': False}))
if st.sidebar.button("🔄 تحديث البيانات"):
    st.cache_data.clear()
    st.rerun()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    st.header(f"👋 أهلاً {name}")
    df = fetch_and_clean_data()
    
    # السجلات التي تظهر للموظف (بدون المراجعات الإدارية)
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = STAFF_DATA[name]['salary']
    total_disc = int(user_records['discount'].sum())
    # حساب المكافآت اليدوية فقط وحجب الأوفر تايم التلقائي
    manual_bonus = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب الأسبوعي", f"{salary:,}")
    c2.metric("إجمالي الخصومات", f"{total_disc:,}")
    # الصافي هنا لا يشمل الأوفر تايم التلقائي بناءً على طلبك
    c3.metric("الصافي (بدون إضافي)", f"{salary - total_disc + manual_bonus:,}")

    st.divider()
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    col_a, col_b = st.columns(2)
    if col_a.button("📥 تسجيل حضور"):
        emp = STAFF_DATA[name]
        start_t_str = emp['start'] if emp['type'] == 'single' else emp['s1']
        t_start = datetime.strptime(start_t_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        disc = int((now - t_start).total_seconds() / 60 * 200) if now > t_start + timedelta(minutes=5) else 0
        send_to_google(name, c_date, c_time, "حضور", disc, 0)
        st.cache_data.clear(); st.success(f"تم الحضور. الخصم: {disc:,}"); time.sleep(1); st.rerun()

    if col_b.button("📤 تسجيل انصراف"):
        emp = STAFF_DATA[name]
        end_t_str = emp['end'] if emp['type'] == 'single' else emp['e2']
        t_end = datetime.strptime(end_t_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        ov = int((now - t_end).total_seconds() / 60 * 100) if now > t_end + timedelta(minutes=1) else 0
        send_to_google(name, c_date, c_time, "انصراف", 0, ov)
        st.cache_data.clear(); st.info("تم تسجيل الانصراف"); time.sleep(1); st.rerun()

    # استرجاع سجل النشاطات للموظف
    with st.expander("📊 سجل نشاطاتي"):
        if not user_records.empty:
            # عرض التوع والخصم والمكافأة فقط (بدون عمود الأوفر تايم الصريح)
            display_df = user_records.copy()
            display_df = display_df[['data', 'type', 'discount', 'overtime']]
            display_df.columns = ['التاريخ/الوقت', 'النوع', 'الخصم', 'المكافأة']
            st.dataframe(display_df, hide_index=True, use_container_width=True)

    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ (إذا سلفة)", min_value=0, step=1000)
        reason = st.text_input("السبب")
        if st.button("إرسال الطلب"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("تم إرسال الطلب")

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.header("👑 لوحة المدير")
    
    with st.expander("👤 إدارة الموظفين (تعديل الأوقات والرواتب)"):
        mode = st.radio("العملية:", ["تعديل موظف حالي", "إضافة موظف جديد"], horizontal=True)
        if mode == "تعديل موظف حالي":
            target = st.selectbox("اختر الموظف:", list(STAFF_DATA.keys()))
            emp = STAFF_DATA[target]
            new_sal = st.number_input("الراتب:", value=emp['salary'], step=5000, key=f"s_{target}")
            new_ps = st.text_input("الرمز:", value=emp['pass'], key=f"p_{target}")
            if emp['type'] == 'single':
                c1, c2 = st.columns(2)
                t_s = c1.text_input("حضور:", value=emp['start'])
                t_e = c2.text_input("انصراف:", value=emp['end'])
                if st.button("حفظ التعديلات"):
                    st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_ps, "start":t_s, "end":t_e})
                    st.success("تم الحفظ"); time.sleep(1); st.rerun()
            else:
                c1, c2, c3, c4 = st.columns(4)
                v1, v2, v3, v4 = c1.text_input("س1", emp['s1']), c2.text_input("إ1", emp['e1']), c3.text_input("س2", emp['s2']), c4.text_input("إ2", emp['e2'])
                if st.button("حفظ التعديلات"):
                    st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_ps, "s1":v1, "e1":v2, "s2":v3, "e2":v4})
                    st.success("تم الحفظ"); time.sleep(1); st.rerun()
        else:
            nn = st.text_input("الاسم الجديد:")
            nsal = st.number_input("الراتب:", step=5000)
            npass = st.text_input("الرمز:")
            ntype = st.selectbox("النوع:", ["single", "double"])
            if st.button("إضافة"):
                if ntype == "single":
                    st.session_state['staff_registry'][nn] = {"salary":nsal, "pass":npass, "start":"15:00", "end":"22:00", "type":"single"}
                else:
                    st.session_state['staff_registry'][nn] = {"salary":nsal, "pass":npass, "s1":"10:00", "e1":"14:00", "s2":"16:00", "e2":"22:00", "type":"double"}
                st.success("تمت الإضافة"); time.sleep(1); st.rerun()

    st.divider()
    df_raw = fetch_and_clean_data()
    
    st.subheader("📩 طلبات الموظفين")
    if not df_raw.empty:
        reqs = df_raw[df_raw['type'].str.contains("طلب", na=False)]
        archived_ids = df_raw[df_raw['type'] == "مؤرشف"]['data'].tolist()
        pending = reqs[~reqs['data'].isin(archived_ids)]
        
        if not pending.empty:
            for i, row in pending[::-1].iterrows():
                with st.expander(f"📌 {row['name']} - {row['type']}"):
                    st.write(f"التفاصيل: {row['data']} | المبلغ: {row['discount']}")
                    ca, cb = st.columns(2)
                    if ca.button("✅ موافقة", key=f"y{i}"):
                        if "سلفة" in row['type']:
                            send_to_google(row['name'], f"سلفة مثبتة: {row['data']}", "---", "سلفة مقبولة", row['discount'], 0)
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()
                    if cb.button("❌ رفض", key=f"n{i}"):
                        send_to_google(row['name'], row['data'], "---", "مؤرشف", 0, 0)
                        st.cache_data.clear(); st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("➕ مكافأة")
        e_m = st.selectbox("الموظف", list(STAFF_DATA.keys()), key="m")
        a_m = st.number_input("المبلغ", step=1000, key="am")
        if st.button("إضافة مكافأة"):
            send_to_google(e_m, "مكافأة يدوية", "---", "مكافأة", 0, a_m)
            st.cache_data.clear(); st.success("تمت"); st.rerun()
    with c2:
        st.subheader("🚫 غياب")
        e_g = st.selectbox("الموظف", list(STAFF_DATA.keys()), key="g")
        a_g = st.number_input("مبلغ الخصم", step=1000, value=15000, key="ag")
        if st.button("تسجيل الخصم"):
            send_to_google(e_g, "غياب يدوي", "---", "غياب", a_g, 0)
            st.cache_data.clear(); st.error("تم الخصم"); st.rerun()

    st.divider()
    if st.button("📊 عرض كشف الرواتب"):
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))

    if st.button("🔄 تصفير الأسبوع"):
        send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.cache_data.clear(); st.balloons(); st.rerun()
