import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import time

# --- الإعدادات الأساسية ---
ADMIN_PASSWORD = "5566"
FORM_URL = "https://docs.google.com/forms/e/1FAIpQLSdDEVeQ9TQnKKZw-owowdOJ1BU6t6i-XtCObOo0iTh_4YKzPg/formResponse"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-53Topnqu23Qtrn1bzNpWa0jVKKuYXyWNukJ0QlNdeBGnC5uH-_mzDEXnn8NkpGu9uLbZDZziaf0s/pub?gid=1287689653&single=true&output=csv"

# قناة الإشعارات (للتنبيه على شاشة القفل بنغمة)
# ملاحظة: يجب تحميل تطبيق ntfy والاشتراك في هذه القناة (topic)
NOTIF_TOPIC = "basma_notifications_2026"

STAFF_DATA = {
    "أمير": {"salary": 115000, "pass": "1122", "start": "16:00", "end": "23:00", "type": "single"},
    "فؤاد": {"salary": 165000, "pass": "1133", "s1": "10:20", "e1": "15:00", "s2": "17:20", "e2": "22:00", "type": "double"},
    "حارث": {"salary": 135000, "pass": "1144", "start": "15:00", "end": "22:00", "type": "single"},
    "ياسر": {"salary": 115000, "pass": "1155", "s1": "10:00", "e1": "13:00", "s2": "15:00", "e2": "23:00", "type": "double"},
    "صادق": {"salary": 75000, "pass": "1166", "start": "15:00", "end": "22:30", "type": "single"},
    "كرار": {"salary": 75000, "pass": "1177", "start": "15:00", "end": "22:30", "type": "single"},
}

# --- وظيفة إرسال إشعار للهاتف ---
def send_push(title, message):
    try:
        requests.post(f"https://ntfy.sh/{NOTIF_TOPIC}", 
            data=message.encode('utf-8'),
            headers={"Title": title.encode('utf-8'), "Priority": "high", "Tags": "bell"})
    except: pass

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
        requests.post(FORM_URL, data=payload, timeout=5)
        return True
    except: return False

@st.cache_data(ttl=5) # تقليل وقت الكاش لضمان سرعة ظهور الطلبات
def fetch_and_clean_data():
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&cache={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        df['name'] = df['name'].fillna("").astype(str).str.strip()
        df['type'] = df['type'].fillna("").astype(str).str.strip()
        df['data'] = df['data'].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0)
        
        # نحدد بداية الأسبوع الحالي
        resets = df[df['type'] == 'تصفية أسبوعية'].index
        active_df = df.iloc[resets.max() + 1:] if not resets.empty else df
        return active_df
    except:
        return pd.DataFrame()

def get_active_financials(name):
    df = fetch_and_clean_data()
    if df.empty: return {"discounts": 0, "overtime": 0, "history": pd.DataFrame()}
    # نستثني فقط الأرشفة والطلبات من حساب الراتب الصافي
    clean_df = df[~df['type'].str.contains("طلب|مؤرشف", na=False)]
    user_data = clean_df[clean_df['name'] == name]
    return {
        "discounts": int(user_data['discount'].sum()),
        "overtime": int(user_data['overtime'].sum()),
        "history": user_data
    }

# --- واجهة التطبيق ---
st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
st.title("🏦 نظام بصمة البسمة")
user_role = st.radio("اختر نوع الدخول:", ["موظف", "المدير"], horizontal=True)

if user_role == "موظف":
    selected_name = st.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    saved_pass_key = f"saved_pass_{selected_name}"
    default_pass = st.session_state.get(saved_pass_key, "")
    entered_pass = st.text_input("الرمز السري:", value=default_pass, type="password")
    
    if st.button("🔓 تسجيل دخول"):
        if entered_pass == STAFF_DATA[selected_name]["pass"]:
            st.session_state['logged_in_user'] = selected_name
            st.rerun()
        else: st.error("الرمز السري خطأ")

    if 'logged_in_user' in st.session_state and st.session_state['logged_in_user'] == selected_name:
        st.success(f"مرحباً بك: {selected_name}")
        fin = get_active_financials(selected_name)
        
        # ... (عرض المربعات المالية) ...
        st.metric("الصافي الحالي", f"{(STAFF_DATA[selected_name]['salary'] - fin['discounts'] + fin['overtime']):,}")

        st.divider()
        now = datetime.now()
        c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

        # --- أزرار الحضور والانصراف مع إشعارات ---
        col1, col2 = st.columns(2)
        if col1.button("📥 حضور"):
            send_to_google(selected_name, c_date, c_time, "حضور", 0, 0)
            send_push("حركة حضور", f"الموظف {selected_name} سجل حضور")
            st.success("تم الإرسال"); time.sleep(1); st.cache_data.clear(); st.rerun()

        st.divider()
        # --- نظام الطلبات المصحح ---
        with st.expander("📝 تقديم طلب (سلفة / إجازة)"):
            t_req = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
            val_req = st.number_input("المبلغ (للسلفة)", min_value=0, step=5000)
            reason = st.text_input("التفاصيل / السبب")
            if st.button("إرسال الطلب الآن"):
                if reason:
                    u_id = f"{reason} | {now.strftime('%H:%M:%S')}"
                    # نرسل "طلب" في خانة الـ type لكي يراها المدير
                    success = send_to_google(selected_name, u_id, c_date, f"طلب {t_req}", val_req, 0)
                    if success:
                        send_push("📩 طلب جديد", f"من {selected_name}: {t_req} - {reason}")
                        st.success("وصل الطلب للمدير بنجاح ✅")
                        time.sleep(1); st.cache_data.clear(); st.rerun()
                else: st.warning("اكتب السبب أولاً")

elif user_role == "المدير":
    admin_pass = st.text_input("رمز المدير:", type="password")
    if admin_pass == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")
        
        # --- عرض الطلبات المعلقة (التصحيح هنا) ---
        st.subheader("📩 طلبات الموظفين الواردة")
        df_all = fetch_and_clean_data()
        if not df_all.empty:
            # نبحث عن أي صف يحتوي نوعه على كلمة "طلب"
            requests_df = df_all[df_all['type'].str.contains("طلب", na=False)]
            # نستبعد ما تمت أرشفته مسبقاً
            archived_list = df_all[df_all['type'] == "مؤرشف"]['data'].tolist()
            pending = requests_df[~requests_df['data'].isin(archived_list)]

            if not pending.empty:
                for idx, row in pending[::-1].iterrows():
                    with st.expander(f"🔴 {row['name']} - {row['type']}"):
                        st.write(f"**التفاصيل:** {row['data']}")
                        st.write(f"**التاريخ:** {row['time']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"y_{idx}"):
                            # تسجيل الحركة كموافقة
                            send_to_google(row['name'], f"موافقة: {row['data']}", "00:00", "حركة مؤكدة", row['discount'] if "سلفة" in row['type'] else 0, 0)
                            # أرشفة الطلب لكي يختفي من القائمة
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            send_push("تم قبول طلبك", f"يا {row['name']}، وافق المدير على طلبك")
                            st.success("تم الحفظ"); time.sleep(0.5); st.rerun()
                        if c2.button("❌ رفض", key=f"n_{idx}"):
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.error("تم الرفض"); time.sleep(0.5); st.rerun()
            else: st.info("لا توجد طلبات جديدة حالياً.")
        
        st.divider()
        # ... بقية لوحة المدير (مكافآت، غياب، كشف رواتب) ...
