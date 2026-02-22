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

def get_active_financials(name):
    try:
        df = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
        df.columns = [c.strip() for c in df.columns]
        df['name'] = df['name'].fillna("").astype(str).str.strip()
        df['type'] = df['type'].fillna("").astype(str).str.strip()
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        df['overtime'] = pd.to_numeric(df['overtime'], errors='coerce').fillna(0)
        
        resets = df[df['type'] == 'تصفية أسبوعية'].index
        active_df = df.iloc[resets.max() + 1:] if not resets.empty else df
        
        # الفلترة: نحسب السطور المالية الحقيقية فقط (تجاهل الطلبات المعالجة أو المعلقة)
        user_data = active_df[(active_df['name'] == name) & 
                             (~active_df['type'].str.contains("طلب", na=False)) & 
                             (~active_df['type'].str.contains("مؤرشف", na=False))]
        
        return {
            "discounts": int(user_data['discount'].sum()),
            "overtime": int(user_data['overtime'].sum())
        }
    except:
        return {"discounts": 0, "overtime": 0}

st.set_page_config(page_title="نظام بصمة البسمة", layout="centered")
user_role = st.sidebar.radio("دخول كـ:", ["موظف", "المدير"])

if user_role == "موظف":
    selected_name = st.sidebar.selectbox("اختر اسمك:", list(STAFF_DATA.keys()))
    entered_pass = st.sidebar.text_input("الرمز السري:", type="password")

    if entered_pass == STAFF_DATA[selected_name]["pass"]:
        st.header(f"👋 أهلاً {selected_name}")
        fin = get_active_financials(selected_name)
        weekly_salary = STAFF_DATA[selected_name]['salary']
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الراتب الأسبوعي", f"{weekly_salary:,}")
        col_m2.metric("إجمالي الخصم", f"{fin['discounts']:,}")
        col_m3.metric("الصافي الحالي", f"{weekly_salary - fin['discounts'] + fin['overtime']:,}")
        
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
            st.success("تم تسجيل الحضور"); time.sleep(1); st.rerun()

        if c2.button("📤 تسجيل انصراف"):
            send_to_google(selected_name, c_date, c_time, "انصراف", 0, 0)
            st.info("تم تسجيل الانصراف بنجاح"); time.sleep(1); st.rerun()

        st.divider()
        with st.expander("📝 طلب إجازة أو سلفة"):
            t_req = st.selectbox("النوع", ["إجازة", "سلفة"])
            val_req = st.number_input("المبلغ (للسلفة فقط)", min_value=0, step=5000)
            reason = st.text_input("السبب")
            if st.button("إرسال الطلب"):
                send_to_google(selected_name, c_date, reason, f"طلب {t_req}", val_req, 0)
                st.warning("تم الإرسال للمدير")

elif user_role == "المدير":
    if st.sidebar.text_input("رمز المدير:", type="password") == ADMIN_PASSWORD:
        st.header("👑 لوحة تحكم المدير")

        st.subheader("📩 طلبات معلقة")
        try:
            df_all = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
            df_all.columns = [c.strip() for c in df_all.columns]
            df_all['type'] = df_all['type'].fillna("").astype(str)
            df_all['discount'] = pd.to_numeric(df_all['discount'], errors='coerce').fillna(0)
            
            # جلب الطلبات فقط وتصفية المعالج منها
            # نعتبر الطلب معالج إذا وجدنا سطر "مؤرشف" بنفس الاسم والبيانات
            reqs = df_all[df_all['type'].str.contains("طلب", na=False)]
            archived = df_all[df_all['type'] == "مؤرشف"]['data'].tolist()
            
            # عرض الطلبات غير المؤرشفة فقط
            pending_reqs = reqs[~reqs['data'].isin(archived)]
            
            if not pending_reqs.empty:
                for idx, row in pending_reqs[::-1].iterrows():
                    with st.expander(f"📌 {row['type']} - {row['name']}"):
                        st.write(f"**التفاصيل:** {row['data']}")
                        c1, c2, c3 = st.columns(3)
                        
                        # زر الموافقة (للسلف فقط يضيف خصم، وللإجازة يؤرشف فقط)
                        if c1.button("✅ موافقة", key=f"ok_{idx}"):
                            if "سلفة" in row['type']:
                                send_to_google(row['name'], f"سلفة: {row['data']}", "00:00", "سلفة مقبولة", row['discount'], 0)
                            # أرشفة الطلب فوراً لكي يختفي
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.success("تمت الموافقة"); time.sleep(1); st.rerun()
                        
                        # زر الرفض
                        if c2.button("❌ رفض", key=f"no_{idx}"):
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.error("تم الرفض والإخفاء"); time.sleep(1); st.rerun()

                        # زر إخفاء (بدون إجراء)
                        if c3.button("👁️ إخفاء", key=f"hide_{idx}"):
                            send_to_google(row['name'], row['data'], "00:00", "مؤرشف", 0, 0)
                            st.info("تم الإخفاء"); time.sleep(1); st.rerun()
            else:
                st.info("القائمة نظيفة، لا توجد طلبات معلقة.")
        except: st.error("خطأ في الاتصال بالبيانات")

        st.divider()
        if st.button("📊 عرض كشف الرواتب المُرتب"):
            try:
                df_rep = pd.read_csv(f"{SHEET_CSV_URL}&t={time.time()}")
                df_rep.columns = [c.strip() for c in df_rep.columns]
                df_rep['discount'] = pd.to_numeric(df_rep['discount'], errors='coerce').fillna(0)
                df_rep['overtime'] = pd.to_numeric(df_rep['overtime'], errors='coerce').fillna(0)
                
                res_idx = df_rep[df_rep['type'] == 'تصفية أسبوعية'].index
                active_df = df_rep.iloc[res_idx.max() + 1:] if not res_idx.empty else df_rep
                
                summary = []
                for name, info in STAFF_DATA.items():
                    u_df = active_df[(active_df['name'] == name.strip()) & 
                                     (~active_df['type'].str.contains("طلب", na=False)) &
                                     (~active_df['type'].str.contains("مؤرشف", na=False))]
                    d, o = int(u_df['discount'].sum()), int(u_df['overtime'].sum())
                    summary.append({"الموظف": name, "الراتب": info['salary'], "الخصم": d, "الإضافي": o, "الصافي": info['salary'] - d + o})
                st.table(pd.DataFrame(summary).sort_values(by="الصافي", ascending=False))
            except: st.error("خطأ في الكشف")

        st.divider()
        if st.button("🔄 تصفير الأسبوع"):
            send_to_google("نظام_تصفير", "تصفية", "00:00", "تصفية أسبوعية", 0, 0)
            st.balloons(); time.sleep(1); st.rerun()
