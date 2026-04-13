import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# حفظ بيانات الموظفين والإعدادات في الـ session_state
if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
        "علي ماجد": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
    }

if 'penalty_rate' not in st.session_state:
    st.session_state['penalty_rate'] = 100  # القيمة الافتراضية لدقيقة التأخير

STAFF_DATA = st.session_state['staff_registry']
PENALTY_RATE = st.session_state['penalty_rate']

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
        for col in ['name', 'type', 'data', 'time']:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        resets = df[df['type'] == "تصفية أسبوعية"].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:].reset_index(drop=True)
        return df
    except: return pd.DataFrame()

# --- واجهة البرنامج (الثيم الحديث) ---
st.set_page_config(page_title="Al-Basma Smart System", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    .stButton>button {{
        border-radius: 20px;
        border: 1px solid #00f2fe;
        background: rgba(0, 242, 254, 0.1);
        color: #00f2fe;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }}
    .stButton>button:hover {{
        background: #00f2fe;
        color: #000;
        box-shadow: 0 0 15px #00f2fe;
    }}
    div[data-testid="stMetricValue"] {{ color: #00f2fe !important; }}
    .stTextInput>div>div>input {{
        background-color: rgba(255,255,255,0.05);
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(0,242,254,0.3);
    }}
    .stSelectbox>div>div {{
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- تسجيل الدخول ---
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>💎 بصمة البسمة الذكية</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1)'>", unsafe_allow_html=True)
        role = st.radio("نوع الصلاحية:", ["موظف", "المدير"], horizontal=True)
        
        if role == "موظف":
            user_sel = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
            user_pass = st.text_input("كلمة المرور:", type="password")
            if st.button("دخول للنظام"):
                if user_pass == STAFF_DATA[user_sel]["pass"]:
                    st.session_state.update({'auth':True, 'user':user_sel, 'role':"موظف"})
                    st.rerun()
                else: st.error("عذراً، الرمز السري غير صحيح")
        else:
            admin_pass = st.text_input("رمز الإدارة:", type="password")
            if st.button("فتح لوحة التحكم"):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.update({'auth':True, 'role':"المدير"})
                    st.rerun()
                else: st.error("عذراً، الرمز السري غير صحيح")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- الشريط الجانبي ---
with st.sidebar:
    st.markdown(f"<h3 style='color:#00f2fe'>👤 {st.session_state.get('user', 'المدير')}</h3>", unsafe_allow_html=True)
    if st.button("🔄 تحديث"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🚪 خروج"):
        st.session_state.update({'auth': False})
        st.rerun()

# --- واجهة الموظف ---
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp_info = STAFF_DATA[name]
    st.markdown(f"<h2 style='text-align: right;'>أهلاً بك، {name} ✨</h2>", unsafe_allow_html=True)
    
    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    
    salary = emp_info['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("الراتب", f"{salary:,}")
    col_m2.metric("الخصومات", f"{total_disc:,}")
    col_m3.metric("الصافي", f"{salary - total_disc + manual_bonuses:,}")

    st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;'>", unsafe_allow_html=True)
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    
    # --- نظام اختيار الشفت للموظفين بنظام Double ---
    shift_to_calc = "start" # الافتراضي للـ single
    display_type = "حضور"

    if emp_info['type'] == 'double':
        st.markdown("##### 🕒 اختر الوجبة الحالية:")
        shift_choice = st.radio("الوجبة:", ["الوجبة الأولى", "الوجبة الثانية"], horizontal=True)
        if shift_choice == "الوجبة الأولى":
            shift_to_calc = "s1"
            display_type = "حضور (شفت 1)"
        else:
            shift_to_calc = "s2"
            display_type = "حضور (شفت 2)"

    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("📥 تسجيل بصمة حضور"):
        start_t_str = emp_info[shift_to_calc]
        t_start = datetime.strptime(start_t_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        
        # حساب الخصم بناءً على المعادلة اليدوية من المدير
        minutes_late = (now - t_start).total_seconds() / 60
        disc = int(minutes_late * PENALTY_RATE) if minutes_late > 5 else 0
        
        send_to_google(name, c_date, c_time, display_type, disc, 0)
        st.success(f"تم تسجيل الحضور بنجاح. التأخير: {int(max(0, minutes_late))} دقيقة")
        st.cache_data.clear(); time.sleep(1); st.rerun()

    if col_btn2.button("📤 تسجيل بصمة انصراف"):
        send_to_google(name, c_date, c_time, "انصراف", 0, 0)
        st.info("تم تسجيل الانصراف. نراك قريباً!")
        st.cache_data.clear(); time.sleep(1); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ (للسلف فقط)", min_value=0, step=1000)
        reason = st.text_input("السبب أو الملاحظات")
        if st.button("إرسال الطلب للمدير"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("تم إرسال طلبك للمراجعة")

# --- واجهة المدير ---
elif st.session_state['role'] == "المدير":
    st.markdown("<h2 style='text-align: center; color: #00f2fe;'>👑 لوحة التحكم بالإدارة</h2>", unsafe_allow_html=True)
    
    # --- تعديل معادلة الخصم ---
    with st.expander("⚙️ إعدادات النظام ومعادلة الخصم"):
        new_rate = st.number_input("سعر دقيقة التأخير (دينار):", value=st.session_state['penalty_rate'], step=25)
        if st.button("حفظ المعادلة الجديدة"):
            st.session_state['penalty_rate'] = new_rate
            st.success(f"تم تغيير الخصم إلى {new_rate} دينار لكل دقيقة تأخير")

    with st.expander("👤 إدارة شؤون الموظفين"):
        mode = st.radio("العملية:", ["تعديل بيانات موظف", "إضافة موظف جديد"], horizontal=True)
        if mode == "تعديل بيانات موظف":
            target = st.selectbox("اختر الموظف:", list(STAFF_DATA.keys()))
            emp = STAFF_DATA[target]
            col_e1, col_e2 = st.columns(2)
            new_sal = col_e1.number_input("الراتب الشهري:", value=emp['salary'], step=5000)
            new_ps = col_e2.text_input("رمز الدخول:", value=emp['pass'])
            
            if emp['type'] == 'single':
                c1, c2 = st.columns(2)
                t_s = c1.text_input("وقت الحضور:", value=emp['start'])
                t_e = c2.text_input("وقت الانصراف:", value=emp['end'])
                if st.button("حفظ التغييرات"):
                    st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_ps, "start":t_s, "end":t_e})
                    st.success("تم التحديث"); time.sleep(1); st.rerun()
            else:
                c1, c2, c3, c4 = st.columns(4)
                v1, v2, v3, v4 = c1.text_input("س1", emp['s1']), c2.text_input("إ1", emp['e1']), c3.text_input("س2", emp['s2']), c4.text_input("إ2", emp['e2'])
                if st.button("حفظ التغييرات"):
                    st.session_state['staff_registry'][target].update({"salary":new_sal, "pass":new_ps, "s1":v1, "e1":v2, "s2":v3, "e2":v4})
                    st.success("تم التحديث"); time.sleep(1); st.rerun()
        else:
            nn = st.text_input("اسم الموظف الثلاثي:")
            nsal = st.number_input("الراتب الافتتاحي:", step=5000)
            npass = st.text_input("تعيين رمز دخول:")
            ntype = st.selectbox("نظام الدوام:", ["single", "double"])
            if st.button("إضافة الموظف"):
                if ntype == "single":
                    st.session_state['staff_registry'][nn] = {"salary":nsal, "pass":npass, "start":"15:00", "end":"22:00", "type":"single"}
                else:
                    st.session_state['staff_registry'][nn] = {"salary":nsal, "pass":npass, "s1":"10:00", "e1":"14:00", "s2":"16:00", "e2":"22:00", "type":"double"}
                st.success("تمت الإضافة بنجاح"); time.sleep(1); st.rerun()

    st.divider()
    df_raw = fetch_and_clean_data()
    
    st.subheader("📩 طلبات قيد الانتظار")
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
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("➕ مكافآت")
        e_m = st.selectbox("اختر الموظف", list(STAFF_DATA.keys()), key="m")
        a_m = st.number_input("مبلغ المكافأة", step=1000, key="am")
        if st.button("تأكيد المكافأة"):
            send_to_google(e_m, "مكافأة إدارية", "---", "مكافأة", 0, a_m)
            st.cache_data.clear(); st.success("تمت الإضافة"); time.sleep(1); st.rerun()
    with col_f2:
        st.subheader("🚫 غيابات")
        e_g = st.selectbox("اختر الموظف", list(STAFF_DATA.keys()), key="g")
        a_g = st.number_input("مبلغ الخصم", step=1000, value=15000, key="ag")
        if st.button("تأكيد الخصم"):
            send_to_google(e_g, "غياب إداري", "---", "غياب", a_g, 0)
            st.cache_data.clear(); st.error("تم تسجيل الخصم"); time.sleep(1); st.rerun()

    st.divider()
    if st.button("📊 توليد كشف الرواتب الأسبوعي"):
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الراتب الأساسي": info['salary'], "إجمالي الخصم": d, "إجمالي الإضافي": o, "الصافي النهائي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))

    if st.button("🗑️ تصفير الأسبوع (أرشفة)"):
        send_to_google("نظام", "تصفير الأسبوع", "00:00", "تصفية أسبوعية", 0, 0)
        st.cache_data.clear(); st.balloons(); time.sleep(1); st.rerun()
