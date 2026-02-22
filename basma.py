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
    try: requests.post(FORM_URL, data=payload, timeout=5)
    except: st.error("فشل في الاتصال بجوجل")

def get_active_data():
    try:
        # كسر الكاش لضمان جلب البيانات الجديدة
        df = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
        if df.empty: return pd.DataFrame()
        
        # البحث عن آخر تصفية
        reset_indices = df[df['type'] == 'تصفية أسبوعية'].index
        if not reset_indices.empty:
            return df.iloc[reset_indices.max() + 1:].copy()
        return df.copy()
    except Exception as e:
        return None # نرجع None لتمييز حالة الخطأ عن حالة الجدول الفارغ

def get_staff_financials(df_active, name):
    if df_active is None or df_active.empty: 
        return {"discounts": 0, "overtime": 0}
    
    target = clean_name(name)
    user_df = df_active[df_active['name'].apply(clean_name) == target]
    return {
        "discounts": int(user_df['discount'].sum()) if 'discount' in user_df else 0,
        "overtime": int(user_df['overtime'].sum()) if 'overtime' in user_df else 0
    }

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

# جلب البيانات مرة واحدة في بداية التشغيل لضمان استقرار العرض
df_active = get_active_data()

if role == "موظف":
    u_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    u_pass = st.sidebar.text_input("الرمز:", type="password")

    if u_pass == STAFF_DATA[u_name]["pass"]:
        st.header(f"👋 أهلاً {u_name}")
        
        if df_active is None:
            st.warning("⚠️ لا يمكن جلب البيانات حالياً، يرجى التحقق من الإنترنت.")
            fin = {"discounts": 0, "overtime": 0}
        else:
            fin = get_staff_financials(df_active, u_name)
            
        sal = STAFF_DATA[u_name]['salary']
        col1, col2, col3 = st.columns(3)
        col1.metric("الراتب", f"{sal:,}")
        col2.metric("الخصومات", f"{fin['discounts']:,}")
        col3.metric("الصافي", f"{sal - fin['discounts']:,}")
        
        st.divider()
        c_btn1, c_btn2 = st.columns(2)
        now = datetime.now()
        if c_btn1.button("📥 تسجيل حضور"):
            emp = STAFF_DATA[u_name]
            st_t = emp['start'] if emp['type'] == 'single' else emp['s1']
            diff = (datetime.strptime(now.strftime("%H:%M"), "%H:%M") - datetime.strptime(st_t, "%H:%M")).total_seconds() / 60
            disc = int(diff * 200) if diff > 5 else 0
            send_to_google(u_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "حضور", disc, 0)
            st.success("تم الحضور"); time.sleep(1); st.rerun()

        if c_btn2.button("📤 تسجيل انصراف"):
            send_to_google(u_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "انصراف", 0, 0)
            st.info("تم الانصراف")

        st.divider()
        st.subheader("📝 تقديم طلب")
        req_type = st.selectbox("نوع الطلب:", ["إجازة", "سلفة"])
        req_val = st.number_input("المبلغ (للسلفة):", min_value=0, step=1000) if req_type == "سلفة" else 0
        req_note = st.text_input("السبب:")
        if st.button("إرسال الطلب"):
            send_to_google(u_name, now.strftime("%Y-%m-%d"), req_note, f"طلب {req_type}", req_val, 0)
            st.warning("تم الإرسال.. بانتظار المدير")

elif role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة المدير")
        
        if df_active is None:
            st.error("❌ فشل الاتصال بقاعدة البيانات. تأكد من نشر الجدول (Publish to Web).")
        else:
            # 1. إدارة الطلبات
            st.subheader("📩 طلبات الموظفين")
            pending = df_active[df_active['type'].str.contains("طلب", na=False)] if not df_active.empty else pd.DataFrame()
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.expander(f"طلب {row['name']} - {row['type']}"):
                        st.write(f"الملاحظات: {row['data']}")
                        cb1, cb2 = st.columns(2)
                        if cb1.button("✅ موافقة", key=f"ok_{idx}"):
                            type_label = "سلفة مقبولة" if "سلفة" in row['type'] else "إجازة مقبولة"
                            send_to_google(row['name'], datetime.now().strftime("%Y-%m-%d"), "تمت الموافقة", type_label, row['discount'], 0)
                            st.success("تمت الموافقة"); time.sleep(1); st.rerun()
                        if cb2.button("❌ رفض", key=f"no_{idx}"):
                            disc_val = 15000 if "إجازة" in row['type'] else 0
                            send_to_google(row['name'], datetime.now().strftime("%Y-%m-%d"), "تم الرفض", "طلب مرفوض", disc_val, 0)
                            st.error("تم الرفض"); time.sleep(1); st.rerun()
            else: st.write("لا توجد طلبات جديدة")

            st.divider()
            # 2. كشف الرواتب
            st.subheader("📊 كشف الرواتب الأسبوعي")
            if st.button("🔄 تحديث وعرض الكشف"):
                rows = []
                for n, d in STAFF_DATA.items():
                    fin = get_staff_financials(df_active, n)
                    rows.append({
                        "الموظف": n, 
                        "الراتب": d['salary'], 
                        "الخصم": fin['discounts'], 
                        "إضافي": fin['overtime'], 
                        "الصافي": d['salary'] - fin['discounts'] + fin['overtime']
                    })
                st.table(pd.DataFrame(rows).sort_values(by="الصافي", ascending=False))

        st.divider()
        if st.button("🔄 تصفير الأسبوع"):
            send_to_google("نظام", datetime.now().strftime("%Y-%m-%d"), "00:00", "تصفية أسبوعية", 0, 0)
            st.balloons(); st.success("تم التصفير"); time.sleep(1); st.rerun()
