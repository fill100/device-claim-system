import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim", layout="wide")

# ส่วนตรวจสอบ Secrets ก่อนรันแอป
if "connections" not in st.secrets:
    st.error("❌ ยังไม่ได้ตั้งค่า URL ใน Secrets (ทำตามขั้นตอนในแชทได้เลยครับ)")
    st.stop()

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลจากแผ่นหลัก (Sheet1 หรือชื่อที่คุณตั้ง)
df = conn.read(ttl="0")

# รายชื่อสาขา (สรุปจากไฟล์ ศูนย์บริการ.csv)
branches = [
    "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", 
    "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี",
    "ขอนแก่น", "ตาก", "เชียงใหม่", "สงขลา", "ประจวบคีรีขันธ์"
]

# ประเภทอุปกรณ์ (อ้างอิงตามไฟล์ที่คุณอัปโหลด)
devices = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS",
    "Android Box", "Monitor Dell", "Dell Pro Tower", "CCTV", "TV Samsung"
]

st.title("📑 JVFS Device Claim System")

# ฟอร์มบันทึกข้อมูล
with st.expander("➕ บันทึกการเคลมใหม่"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            d_type = st.selectbox("ประเภทอุปกรณ์", devices)
            branch = st.selectbox("สาขา", branches)
            asset = st.text_input("Asset No.")
            sn_old = st.text_input("S/N เครื่องที่เสีย")
        with c2:
            status = st.selectbox("สถานะ", ["Pending", "In Progress", "Done"])
            symptom = st.text_area("อาการเสีย")
            sn_new = st.text_input("S/N เครื่องใหม่ (ถ้ามี)")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            new_data = pd.DataFrame([{
                "วันที่บันทึก": datetime.now().strftime("%d/%m/%Y"),
                "ประเภทอุปกรณ์": d_type,
                "สาขา": branch,
                "Asset No.": asset,
                "S/N เครื่องเสีย": sn_old,
                "อาการ": symptom,
                "สถานะ": status,
                "S/N เครื่องใหม่": sn_new
            }])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success("บันทึกเรียบร้อย!")
            st.rerun()

st.divider()
st.subheader("📊 รายการทั้งหมด")
st.dataframe(df, use_container_width=True)
