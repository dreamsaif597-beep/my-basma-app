import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# --- [تعديل 1] الثيم الجميل والحديث ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');

:root {
    --bg-main: #0a0f1e;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent: #3b82f6;
    --accent2: #6366f1;
    --accent-glow: rgba(59,130,246,0.18);
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --border: rgba(255,255,255,0.07);
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --radius: 14px;
}

html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    direction: rtl;
}

/* --- صفحة الدخول --- */
h1, h2, h3 {
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}

/* --- الحاوية الرئيسية --- */
.block-container {
    padding: 2rem 1.5rem !important;
    max-width: 860px !important;
}

/* --- البطاقات والـ expanders --- */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    padding: 0.85rem 1.1rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* --- المقاييس (Metrics) --- */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1rem !important;
    text-align: center;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, var(--accent-glow), transparent 70%);
    pointer-events: none;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
}

/* --- الأزرار --- */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.25) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.4) !important;
}
.stButton > button[kind="secondary"], .stButton > button:contains("خروج") {
    background: var(--bg-card2) !important;
    box-shadow: none !important;
}

/* --- الإدخالات --- */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* --- الجداول --- */
[data-testid="stTable"] table {
    background: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
    width: 100% !important;
}
[data-testid="stTable"] th {
    background: var(--bg-card2) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.65rem 0.8rem !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTable"] td {
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0.6rem 0.8rem !important;
    font-size: 0.88rem !important;
}
[data-testid="stTable"] tr:hover td {
    background: var(--bg-card2) !important;
}

/* --- الـ Radio والـ Selectbox --- */
.stRadio label, .stSelectbox label {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
}
.stRadio > div > label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.35rem 0.85rem !important;
    transition: all 0.15s;
}
.stRadio > div > label:has(input:checked) {
    border-color: var(--accent) !important;
    background: var(--accent-glow) !important;
}

/* --- الـ Divider --- */
hr {
    border-color: var(--border) !important;
    margin: 1.25rem 0 !important;
}

/* --- Success / Error / Info / Warning --- */
.stSuccess, .stAlert[kind="success"] {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 10px !important;
    color: #6ee7b7 !important;
}
.stError, .stAlert[kind="error"] {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 10px !important;
    color: #fca5a5 !important;
}
.stInfo, .stAlert[kind="info"] {
    background: rgba(59,130,246,0.08) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
}
.stWarning, .stAlert[kind="warning"] {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 10px !important;
    color: #fcd34d !important;
}

/* --- إخفاء السايدبار نهائياً --- */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
    display: none !important;
    width: 0 !important;
}

/* --- أزرار الخروج والتحديث --- */
.top-action-btn button {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
    padding: 0.35rem 0.9rem !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    width: auto !important;
}
.top-action-btn button:hover {
    border-color: var(--accent) !important;
    color: var(--text-primary) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* --- عنوان الصفحة الرئيسي --- */
.main-header {
    background: linear-gradient(135deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(99,102,241,0.15), transparent 70%);
    pointer-events: none;
}
.main-header h2 {
    margin: 0;
    font-size: 1.5rem;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-header p {
    margin: 0.3rem 0 0;
    color: var(--text-muted);
    font-size: 0.85rem;
}

/* --- بادج الشفت --- */
.shift-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    background: var(--accent-glow);
    border: 1px solid rgba(59,130,246,0.3);
    color: var(--accent);
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# حفظ بيانات الموظفين في الـ session_state
if 'staff_registry' not in st.session_state:
    st.session_state['staff_registry'] = {
        "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
        "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
        "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
        "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
        "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
        "علي ماجد": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
    }

# --- [تعديل 3] حفظ إعدادات معادلة الخصم ---
if 'deduction_settings' not in st.session_state:
    st.session_state['deduction_settings'] = {
        "rate_per_minute": 100,   # IQD لكل دقيقة تأخير
        "grace_minutes": 5,       # دقائق السماح
    }

STAFF_DATA = st.session_state['staff_registry']

def get_iraq_time():
    return datetime.utcnow() + timedelta(hours=3)

def send_to_google(name, data_val, time_val, type_val, discount=0, overtime=0, location=""):
    payload = {
        "entry.104291709": name,
        "entry.786801446": data_val,
        "entry.2093200411": time_val,
        "entry.1043553703": type_val,
        "entry.1254543219": int(discount),
        "entry.1151470082": int(overtime),
        "entry.669980309": location,
    }
    try: requests.post(FORM_URL, data=payload, timeout=7)
    except: st.error("فشل الاتصال بجوجل")

@st.cache_data(ttl=2)
def fetch_and_clean_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&nocache={time.time()}")
        df.columns = [c.strip() for c in df.columns]

        # إعادة تسمية الأعمدة بالأسماء الصحيحة حسب الترتيب الفعلي في الشيت
        # الشيت: طابع زمني | name | data | time | type | discount | overtime | النتيجة | الموقع الجغرافي | العمود 9
        col_map = {}
        cols = list(df.columns)
        if len(cols) >= 1: col_map[cols[0]] = 'timestamp'
        if len(cols) >= 2: col_map[cols[1]] = 'name'
        if len(cols) >= 3: col_map[cols[2]] = 'data'
        if len(cols) >= 4: col_map[cols[3]] = 'time'
        if len(cols) >= 5: col_map[cols[4]] = 'type'
        if len(cols) >= 6: col_map[cols[5]] = 'discount'
        if len(cols) >= 7: col_map[cols[6]] = 'overtime'
        if len(cols) >= 9: col_map[cols[8]] = 'location'
        df = df.rename(columns=col_map)

        for col in ['name', 'type', 'data', 'time']:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0).astype(int)
        if 'location' not in df.columns:
            df['location'] = ""
        else:
            df['location'] = df['location'].fillna("").astype(str).str.strip()

        resets = df[df['type'] == "تصفية أسبوعية"].index
        if not resets.empty:
            df = df.iloc[resets.max() + 1:].reset_index(drop=True)
        return df
    except: return pd.DataFrame()

# --- واجهة البرنامج ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered", initial_sidebar_state="collapsed")

if 'auth' not in st.session_state: st.session_state['auth'] = False

# ========== صفحة الدخول ==========
if not st.session_state['auth']:
    st.markdown("""
    <div class="main-header">
        <h2>🌟 نظام بصمة البسمة</h2>
        <p>نظام إدارة الحضور والانصراف</p>
    </div>
    """, unsafe_allow_html=True)

    role = st.radio("الدخول كـ:", ["موظف", "المدير"], horizontal=True)
    if role == "موظف":
        user_sel = st.selectbox("اسم الموظف:", list(STAFF_DATA.keys()))

        # قراءة الرمز المحفوظ من query params إذا موجود
        saved_key = f"saved_pass_{user_sel}"
        default_pass = st.session_state.get(saved_key, "")

        user_pass = st.text_input("الرمز السري:", type="password", value=default_pass)
        remember_me = st.checkbox("تذكر الرمز على هذا الجهاز", value=(default_pass != ""))

        if st.button("دخول الموظف"):
            if user_pass == STAFF_DATA[user_sel]["pass"]:
                if remember_me:
                    st.session_state[saved_key] = user_pass
                else:
                    st.session_state.pop(saved_key, None)
                st.session_state.update({'auth': True, 'user': user_sel, 'role': "موظف"})
                st.rerun()
            else:
                st.error("الرمز خطأ!")
    else:
        saved_admin = st.session_state.get("saved_admin_pass", "")
        admin_pass = st.text_input("رمز المدير:", type="password", value=saved_admin)
        remember_admin = st.checkbox("تذكر الرمز على هذا الجهاز", value=(saved_admin != ""))

        if st.button("دخول المدير"):
            if admin_pass == ADMIN_PASSWORD:
                if remember_admin:
                    st.session_state["saved_admin_pass"] = admin_pass
                else:
                    st.session_state.pop("saved_admin_pass", None)
                st.session_state.update({'auth': True, 'role': "المدير"})
                st.rerun()
            else:
                st.error("الرمز خطأ!")
    st.stop()

col_logout, col_refresh, col_forget, col_spacer = st.columns([1, 1, 1.5, 2.5])
if col_logout.button("🚪 خروج"):
    st.session_state.update({'auth': False})
    st.rerun()
if col_refresh.button("🔄 تحديث"):
    st.cache_data.clear()
    st.rerun()
if col_forget.button("🗝️ نسيان الرمز"):
    # حذف كل الرموز المحفوظة
    keys_to_del = [k for k in st.session_state if k.startswith("saved_")]
    for k in keys_to_del:
        del st.session_state[k]
    st.session_state.update({'auth': False})
    st.rerun()

# ========== واجهة الموظف ==========
if st.session_state['role'] == "موظف":
    name = st.session_state['user']
    emp = STAFF_DATA[name]
    now = get_iraq_time()
    c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    st.markdown(f"""
    <div class="main-header">
        <h2>👋 أهلاً، {name}</h2>
        <p>{now.strftime("%A")} — {c_date} — {c_time}</p>
    </div>
    """, unsafe_allow_html=True)

    df = fetch_and_clean_data()
    user_records = df[(df['name'] == name) & (~df['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"]))]
    salary = emp['salary']
    total_disc = int(user_records['discount'].sum())
    manual_bonuses = int(user_records[user_records['type'] == "مكافأة"]['overtime'].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("الراتب", f"{salary:,}")
    c2.metric("الخصم/السلف", f"{total_disc:,}")
    c3.metric("الصافي", f"{salary - total_disc + manual_bonuses:,}")

    st.divider()

    # --- [تعديل 2] اختيار الشفت للموظفين ذوي الشفتين ---
    if emp['type'] == 'double':
        st.markdown(f"""
        <div class="shift-badge">موظف شفتين</div>
        """, unsafe_allow_html=True)
        shift_choice = st.radio(
            "اختر الشفت:",
            ["الشفت الأول", "الشفت الثاني"],
            horizontal=True,
            key="shift_selector"
        )
        if shift_choice == "الشفت الأول":
            active_start = emp['s1']
            active_end   = emp['e1']
        else:
            active_start = emp['s2']
            active_end   = emp['e2']
        st.caption(f"🕐 وقت الحضور: {active_start} — الانصراف: {active_end}")
    else:
        active_start = emp['start']
        active_end   = emp['end']
        shift_choice = "الشفت الوحيد"

    # --- مكوّن الموقع الجغرافي ---
    # قراءة الموقع من query_params إذا وصل
    _lat = st.query_params.get("lat", "")
    _lon = st.query_params.get("lon", "")
    _geo_err = st.query_params.get("geo_err", "")

    if _lat and _lon:
        st.session_state['geo_lat'] = _lat
        st.session_state['geo_lon'] = _lon
        st.session_state['geo_err'] = ""

    if _geo_err:
        st.session_state['geo_err'] = _geo_err

    lat = st.session_state.get('geo_lat', "")
    lon = st.session_state.get('geo_lon', "")
    geo_err = st.session_state.get('geo_err', "")

    if lat and lon:
        st.caption(f"📍 موقعك محدد: {float(lat):.5f}, {float(lon):.5f}")
    elif geo_err == "denied":
        st.caption("📍 الموقع: تم رفض الإذن")
    else:
        st.caption("📍 الموقع الجغرافي: جاري التحديد...")

    # مكوّن JS يطلب الموقع ويعيد التوجيه مع الإحداثيات في الـ URL
    _has_loc = "true" if (lat and lon) else "false"
    st.components.v1.html(f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
    <button id="geo-btn" onclick="getGeo()" style="
        background:#1a2235;border:1px solid rgba(59,130,246,0.4);
        border-radius:8px;color:#93c5fd;font-size:0.82rem;
        padding:0.3rem 1rem;cursor:pointer;font-family:sans-serif;">
        📡 تحديث الموقع
    </button>
    <span id="status" style="font-size:0.78rem;color:#94a3b8;margin-right:8px;"></span>
    <script>
    var hasLoc = {_has_loc};

    function getGeo() {{
        document.getElementById('status').innerText = 'جاري تحديد الموقع...';
        if (!navigator.geolocation) {{
            redirect('geo_err=unsupported');
            return;
        }}
        navigator.geolocation.getCurrentPosition(
            function(pos) {{
                var la = pos.coords.latitude.toFixed(6);
                var lo = pos.coords.longitude.toFixed(6);
                document.getElementById('status').innerText = '✓ تم: ' + la + ', ' + lo;
                redirect('lat=' + la + '&lon=' + lo);
            }},
            function(err) {{
                document.getElementById('status').innerText = 'تعذر تحديد الموقع';
                redirect('geo_err=denied');
            }},
            {{enableHighAccuracy: true, timeout: 15000, maximumAge: 0}}
        );
    }}

    function redirect(params) {{
        var base = window.parent.location.pathname;
        window.parent.location.replace(base + '?' + params);
    }}

    // تشغيل تلقائي عند أول فتح فقط
    if (!hasLoc) {{
        setTimeout(getGeo, 500);
    }}
    </script>
    </body>
    </html>
    """, height=50)

    if geo_err == "denied":
        st.warning("⚠️ تم رفض إذن الموقع — سيُسجَّل الحضور بدون إحداثيات")
    elif geo_err == "unsupported":
        st.warning("⚠️ المتصفح لا يدعم تحديد الموقع")

    col_a, col_b = st.columns(2)

    if col_a.button("📥 تسجيل حضور"):
        ds = st.session_state['deduction_settings']
        t_start = datetime.strptime(active_start, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        late_mins = (now - t_start).total_seconds() / 60
        if late_mins > ds['grace_minutes']:
            disc = int(late_mins * ds['rate_per_minute'])
        else:
            disc = 0

        # الموقع يُرسل منفصلاً وليس مدموجاً في الملاحظة
        geo_str = f"{lat},{lon}" if lat and lon else ""
        note = f"{c_date}" if emp['type'] == 'single' else f"{c_date} ({shift_choice})"
        send_to_google(name, note, c_time, "حضور", disc, 0, location=geo_str)
        st.cache_data.clear()

        # --- حفظ بيانات الرسالة في session_state لعرضها كـ popup ---
        late_mins_rounded = max(0, int(late_mins))
        shift_label = shift_choice if emp['type'] == 'double' else "الشفت"
        st.session_state['attendance_popup'] = {
            "show": True,
            "disc": disc,
            "name": name,
            "c_date": c_date,
            "c_time": c_time,
            "shift_label": shift_label,
            "active_start": active_start,
            "late_mins": late_mins_rounded,
            "lat": lat,
            "lon": lon,
        }

    if col_b.button("📤 تسجيل انصراف"):
        t_end = datetime.strptime(active_end, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        ov = int((now - t_end).total_seconds() / 60 * 100) if now > t_end + timedelta(minutes=1) else 0
        note = f"{c_date}" if emp['type'] == 'single' else f"{c_date} ({shift_choice})"
        send_to_google(name, note, c_time, "انصراف", 0, ov)
        st.cache_data.clear()
        st.info("تم تسجيل الانصراف 👋")
        time.sleep(1); st.rerun()

    # ========== Popup تفاصيل البصمة ==========
    if st.session_state.get('attendance_popup', {}).get('show'):
        p = st.session_state['attendance_popup']

        @st.dialog("📋 تفاصيل البصمة")
        def show_popup():
            geo_line = f"📍 الموقع: <b>{p.get('lat','')}, {p.get('lon','')}</b><br>" if p.get('lat') else "📍 الموقع: <b style='color:#fbbf24;'>غير محدد</b><br>"
            if p['disc'] == 0:
                st.markdown(f"""
                <div style="text-align:right;direction:rtl;line-height:2.1;font-size:0.92rem;">
                  <div style="font-size:1rem;font-weight:700;color:#10b981;margin-bottom:0.8rem;">أحسنت أيها الموظف النشيط! 🌟</div>
                  👤 الاسم: <b>{p['name']}</b><br>
                  📅 التاريخ: <b>{p['c_date']}</b><br>
                  🕐 وقت الحضور: <b>{p['c_time']}</b><br>
                  📌 الشفت: <b>{p['shift_label']}</b><br>
                  ⏰ وقت الدوام: <b>{p['active_start']}</b><br>
                  {geo_line}
                  ✅ الحالة: <b style="color:#10b981;">في الوقت — لا يوجد خصم</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align:right;direction:rtl;line-height:2.1;font-size:0.92rem;">
                  👤 الاسم: <b>{p['name']}</b><br>
                  📅 التاريخ: <b>{p['c_date']}</b><br>
                  🕐 وقت الحضور الفعلي: <b>{p['c_time']}</b><br>
                  📌 الشفت: <b>{p['shift_label']}</b><br>
                  ⏰ وقت الدوام المقرر: <b>{p['active_start']}</b><br>
                  {geo_line}
                  ⏱️ مدة التأخير: <b style="color:#fbbf24;">{p['late_mins']} دقيقة</b><br>
                  💸 خصم التأخير: <b style="color:#fca5a5;">{p['disc']:,} د.ع</b>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✔️ تم", use_container_width=True):
                st.session_state['attendance_popup'] = {"show": False}
                st.rerun()

        show_popup()

    with st.expander("📊 سجل الحركات"):
        if not user_records.empty:
            view_df = user_records.copy()
            view_df['التاريخ والوقت'] = view_df['data'] + " | " + view_df['time']
            view_df['المكافأة'] = view_df.apply(lambda x: x['overtime'] if x['type'] == "مكافأة" else 0, axis=1)
            final_view = view_df[['التاريخ والوقت', 'type', 'discount', 'المكافأة']]
            final_view.columns = ['التاريخ والوقت', 'العملية', 'الخصم', 'المكافأة']
            st.table(final_view)
        else:
            st.info("لا توجد حركات مسجلة حالياً")

    with st.expander("📝 طلب سلفة أو إجازة"):
        t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
        amt_req = st.number_input("المبلغ (إذا سلفة)", min_value=0, step=1000)
        reason = st.text_input("السبب")
        if st.button("إرسال الطلب"):
            send_to_google(name, f"{reason}", c_date, f"طلب {t_req}", amt_req, 0)
            st.warning("تم إرسال الطلب 📨")

# ========== واجهة المدير ==========
elif st.session_state['role'] == "المدير":
    st.markdown("""
    <div class="main-header">
        <h2>👑 لوحة تحكم المدير</h2>
        <p>إدارة الموظفين والرواتب والخصومات</p>
    </div>
    """, unsafe_allow_html=True)

    # --- [تعديل 3] إعدادات معادلة الخصم ---
    with st.expander("⚙️ إعدادات معادلة الخصم"):
        st.markdown("**تحكم يدوي بحساب خصم التأخير**")
        ds = st.session_state['deduction_settings']
        col1, col2 = st.columns(2)
        new_rate = col1.number_input(
            "مبلغ الخصم لكل دقيقة تأخير (IQD)",
            min_value=0,
            step=25,
            value=ds['rate_per_minute'],
            help="مثال: 100 يعني كل دقيقة تأخير = 100 دينار خصم"
        )
        new_grace = col2.number_input(
            "دقائق السماح (Grace Period)",
            min_value=0,
            step=1,
            value=ds['grace_minutes'],
            help="عدد الدقائق المسموح بها قبل بدء الخصم"
        )
        if st.button("💾 حفظ إعدادات الخصم"):
            st.session_state['deduction_settings']['rate_per_minute'] = new_rate
            st.session_state['deduction_settings']['grace_minutes'] = new_grace
            st.success(f"تم الحفظ ✅  |  {new_rate} د.ع/دقيقة — سماح {new_grace} دقيقة")

        # معاينة المعادلة
        preview_late = st.slider("معاينة: كم دقيقة تأخير؟", 0, 60, 10)
        if preview_late > new_grace:
            preview_disc = (preview_late) * new_rate
            st.info(f"تأخير {preview_late} دقيقة → خصم: **{preview_disc:,} د.ع**")
        else:
            st.info(f"تأخير {preview_late} دقيقة → ضمن وقت السماح، لا خصم")

    with st.expander("👤 إدارة الموظفين"):
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
                    st.session_state['staff_registry'][target].update({"salary": new_sal, "pass": new_ps, "start": t_s, "end": t_e})
                    st.success("تم الحفظ"); time.sleep(1); st.rerun()
            else:
                c1, c2, c3, c4 = st.columns(4)
                v1 = c1.text_input("بداية ش1", emp['s1'])
                v2 = c2.text_input("نهاية ش1", emp['e1'])
                v3 = c3.text_input("بداية ش2", emp['s2'])
                v4 = c4.text_input("نهاية ش2", emp['e2'])
                if st.button("حفظ التعديلات"):
                    st.session_state['staff_registry'][target].update({"salary": new_sal, "pass": new_ps, "s1": v1, "e1": v2, "s2": v3, "e2": v4})
                    st.success("تم الحفظ"); time.sleep(1); st.rerun()
        else:
            nn = st.text_input("الاسم الجديد:")
            nsal = st.number_input("الراتب:", step=5000)
            npass = st.text_input("الرمز:")
            ntype = st.selectbox("النوع:", ["single", "double"])
            if st.button("إضافة"):
                if ntype == "single":
                    st.session_state['staff_registry'][nn] = {"salary": nsal, "pass": npass, "start": "15:00", "end": "22:00", "type": "single"}
                else:
                    st.session_state['staff_registry'][nn] = {"salary": nsal, "pass": npass, "s1": "10:00", "e1": "14:00", "s2": "16:00", "e2": "22:00", "type": "double"}
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
            st.cache_data.clear(); st.success("تمت ✅"); st.rerun()
    with c2:
        st.subheader("🚫 غياب")
        e_g = st.selectbox("الموظف", list(STAFF_DATA.keys()), key="g")
        a_g = st.number_input("مبلغ الخصم", step=1000, value=15000, key="ag")
        if st.button("تسجيل الخصم"):
            send_to_google(e_g, "غياب يدوي", "---", "غياب", a_g, 0)
            st.cache_data.clear(); st.error("تم الخصم"); st.rerun()

    # --- قسم حذف خصم ---
    st.divider()
    with st.expander("🗑️ حذف خصم لموظف"):
        e_del = st.selectbox("اختر الموظف", list(STAFF_DATA.keys()), key="del_emp")

        # جلب خصومات الموظف المختار
        emp_discounts = df_raw[
            (df_raw['name'] == e_del) &
            (df_raw['discount'] > 0) &
            (~df_raw['type'].isin(["مؤرشف", "طلب إجازة", "طلب سلفة"]))
        ].copy()

        if emp_discounts.empty:
            st.info(f"لا توجد خصومات مسجلة لـ {e_del}")
        else:
            st.markdown(f"**خصومات {e_del} الحالية:**")

            for i, row in emp_discounts.iterrows():
                col_info, col_btn = st.columns([4, 1])
                col_info.markdown(
                    f"<div style='background:var(--bg-card2);border:1px solid var(--border);border-radius:10px;"
                    f"padding:0.5rem 0.8rem;font-size:0.85rem;direction:rtl;'>"
                    f"📅 {row['data']} &nbsp;|&nbsp; 🕐 {row['time']} &nbsp;|&nbsp; "
                    f"📋 {row['type']} &nbsp;|&nbsp; 💸 <b style='color:#fca5a5;'>{int(row['discount']):,} د.ع</b>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if col_btn.button("حذف", key=f"del_{i}"):
                    # الحذف يتم بإرسال سجل "إلغاء خصم" بقيمة سالبة تعادل الخصم المراد حذفه
                    send_to_google(
                        e_del,
                        f"إلغاء خصم: {row['data']}",
                        "---",
                        "إلغاء خصم",
                        -int(row['discount']),
                        0
                    )
                    st.cache_data.clear()
                    st.success(f"✅ تم إلغاء خصم {int(row['discount']):,} د.ع")
                    time.sleep(1); st.rerun()
    # --- قسم مواقع الحضور ---
    with st.expander("🗺️ مواقع حضور الموظفين"):
        # فلترة سجلات الحضور التي تحتوي على موقع
        if not df_raw.empty and 'location' in df_raw.columns:
            loc_rows = df_raw[
                (df_raw['type'] == "حضور") &
                (df_raw['location'].str.strip() != "") &
                (df_raw['location'].notna())
            ].copy()

            if loc_rows.empty:
                st.info("لا توجد بصمات مسجلة بموقع جغرافي بعد")
            else:
                # فلتر باسم الموظف
                emp_filter = st.selectbox(
                    "تصفية حسب الموظف:",
                    ["الكل"] + list(STAFF_DATA.keys()),
                    key="loc_filter"
                )
                if emp_filter != "الكل":
                    loc_rows = loc_rows[loc_rows['name'] == emp_filter]

                st.markdown(f"<div style='color:var(--text-muted);font-size:0.83rem;margin-bottom:0.5rem;'>إجمالي البصمات: {len(loc_rows)}</div>", unsafe_allow_html=True)

                for _, row in loc_rows[::-1].iterrows():
                    try:
                        coords = str(row['location']).strip()
                        lat_v, lon_v = coords.split(",")
                        maps_url = f"https://www.google.com/maps?q={lat_v.strip()},{lon_v.strip()}"

                        st.markdown(f"""
                        <div style="background:var(--bg-card2);border:1px solid var(--border);
                            border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.5rem;
                            direction:rtl;font-size:0.86rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                                <div style="color:var(--text-primary);">
                                    👤 <b>{row['name']}</b> &nbsp;|&nbsp;
                                    📅 {row['data']} &nbsp;|&nbsp;
                                    🕐 {row['time']}
                                </div>
                                <a href="{maps_url}" target="_blank" style="
                                    background:linear-gradient(135deg,#3b82f6,#6366f1);
                                    color:#fff;text-decoration:none;border-radius:8px;
                                    padding:0.3rem 0.85rem;font-size:0.8rem;font-weight:600;
                                    white-space:nowrap;">
                                    📍 فتح الموقع
                                </a>
                            </div>
                            <div style="color:var(--text-muted);font-size:0.78rem;margin-top:0.35rem;">
                                إحداثيات: {lat_v.strip()}, {lon_v.strip()}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        pass
        else:
            st.info("لا توجد بيانات موقع — تأكد أن الموظفين سجلوا الحضور مع تفعيل الموقع")

    if st.button("📊 عرض كشف الرواتب"):
        clean = df_raw[~df_raw['type'].isin(["طلب إجازة", "طلب سلفة", "مؤرشف"])]
        totals = clean.groupby('name')[['discount', 'overtime']].sum()

        # ملخص الرواتب
        res = []
        for n, info in STAFF_DATA.items():
            d = int(totals.loc[n, 'discount']) if n in totals.index else 0
            o = int(totals.loc[n, 'overtime']) if n in totals.index else 0
            res.append({"الموظف": n, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
        st.table(pd.DataFrame(res))

        # توقيتات الحضور الفعلية لكل موظف
        st.markdown("### 🕐 توقيتات الحضور الفعلية")
        attendance_rows = clean[clean['type'] == "حضور"][['name', 'data', 'time', 'discount']].copy()
        attendance_rows.columns = ['الموظف', 'التاريخ', 'وقت الحضور', 'الخصم (د.ع)']

        if not attendance_rows.empty:
            # عرض مجمّع لكل موظف في expander منفصل
            for emp_name in STAFF_DATA.keys():
                emp_att = attendance_rows[attendance_rows['الموظف'] == emp_name].copy()
                if not emp_att.empty:
                    total_emp_disc = int(emp_att['الخصم (د.ع)'].sum())
                    days_count = len(emp_att)
                    with st.expander(f"👤 {emp_name}  —  {days_count} يوم  |  إجمالي خصم التأخير: {total_emp_disc:,} د.ع"):
                        display_att = emp_att[['التاريخ', 'وقت الحضور', 'الخصم (د.ع)']].reset_index(drop=True)
                        # إضافة عمود الحالة
                        def status_label(row):
                            emp_info = STAFF_DATA[emp_name]
                            shift_note = str(row['التاريخ'])
                            if emp_info['type'] == 'double':
                                if 'الشفت الثاني' in shift_note:
                                    expected = emp_info['s2']
                                else:
                                    expected = emp_info['s1']
                            else:
                                expected = emp_info['start']
                            disc_val = int(row['الخصم (د.ع)'])
                            if disc_val == 0:
                                return "✅ في الوقت"
                            else:
                                # حساب دقائق التأخير
                                try:
                                    t_exp = datetime.strptime(expected, "%H:%M")
                                    t_act = datetime.strptime(str(row['وقت الحضور']), "%H:%M")
                                    late = int((t_act - t_exp).total_seconds() / 60)
                                    return f"⚠️ متأخر {late} د"
                                except:
                                    return "⚠️ متأخر"
                        display_att['الحالة'] = emp_att.apply(status_label, axis=1)
                        st.table(display_att)
                else:
                    pass  # موظف بدون سجلات حضور لا يظهر
        else:
            st.info("لا توجد سجلات حضور في هذه الفترة")

    if st.button("🔄 تصفير الأسبوع"):
        send_to_google("نظام", "تصفير", "00:00", "تصفية أسبوعية", 0, 0)
        st.cache_data.clear(); st.balloons(); st.rerun()
