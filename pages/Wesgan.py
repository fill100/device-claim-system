import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Wesgan System", layout="wide")

# เชื่อมต่อฐานข้อมูล (ถ้าใช้คนละไฟล์ ให้ระบุ connection name ใหม่ใน secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🛡️ ระบบจัดการอุปกรณ์นอกระบบ (Wesgan)")
st.info("ระบบนี้แยกฐานข้อมูลจาก JVFS Device Claim เพื่อความชัดเจนในการจัดการ")

# --- โครงสร้างคอลัมน์ของ Wesgan (ปรับเปลี่ยนได้ตามต้องการ) ---
WESGAN_COLUMNS = [
    "วันที่รับแจ้ง", "ชื่ออุปกรณ์", "S/N", "อาการเสีย", "ผู้รับผิดชอบ", "สถานะ"
]

# ดึงข้อมูลจาก Tab ชื่อ Wesgan (อย่าลืมไปสร้าง Tab นี้ใน Google Sheets นะครับ)
try:
    df_wesgan = conn.read(worksheet="Wesgan", ttl="0")
    if df_wesgan is None or df_wesgan.empty:
        df_wesgan = pd.DataFrame(columns=WESGAN_COLUMNS)
except:
    st.warning("⚠️ ไม่พบ Worksheet 'Wesgan' กำลังสร้างโครงสร้างข้อมูลให้...")
    df_wesgan = pd.DataFrame(columns=WESGAN_COLUMNS)

# --- ส่วนของการเพิ่มข้อมูล Wesgan ---
with st.expander("➕ เพิ่มอุปกรณ์ Wesgan"):
    with st.form("wesgan_add"):
        c1, c2 = st.columns(2)
        with c1:
            device_name = st.text_input("ชื่ออุปกรณ์")
            sn = st.text_input("Serial Number")
        with c2:
            issue = st.text_area("อาการเสีย")
            owner = st.text_input("ผู้รับผิดชอบ")
            
        if st.form_submit_button("บันทึกข้อมูล Wesgan"):
            new_row = pd.DataFrame([{
                "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ชื่ออุปกรณ์": device_name,
                "S/N": sn,
                "อาการเสีย": issue,
                "ผู้รับผิดชอบ": owner,
                "สถานะ": "Pending"
            }])
            updated_df = pd.concat([df_wesgan, new_row], ignore_index=True)
            conn.update(worksheet="Wesgan", data=updated_df.astype(str))
            st.success("บันทึกข้อมูล Wesgan สำเร็จ!")
            st.rerun()

# --- แสดงตารางข้อมูล Wesgan ---
st.divider()
st.subheader("🔍 ข้อมูลอุปกรณ์ Wesgan ทั้งหมด")
st.dataframe(df_wesgan, use_container_width=True, hide_index=True)
