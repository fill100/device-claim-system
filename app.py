import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. รายชื่อ Sheet ทั้งหมดที่มีในไฟล์ของคุณ (แก้ชื่อให้ตรงกับใน Google Sheets ของคุณ)
AVAILABLE_SHEETS = ["Sheet1", "Sheet2", "Sheet3"] 

# 2. เพิ่มตัวเลือกใน Sidebar เพื่อเลือก Sheet
st.sidebar.title("📁 การจัดการข้อมูล")
selected_sheet = st.sidebar.selectbox("เลือก Worksheet ที่ต้องการใช้งาน:", AVAILABLE_SHEETS)

# กำหนดชื่อคอลัมน์มาตรฐาน
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "แก้ในTrackMo"
]

# ดึงข้อมูลจาก Sheet ที่เลือก
try:
    # เพิ่มพารามิเตอร์ worksheet เข้าไป
    df = conn.read(worksheet=selected_sheet, ttl="0")
    
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ Worksheet '{selected_sheet}' ขาดคอลัมน์: {', '.join(missing_cols)}")
            for col in missing_cols:
                df[col] = ""
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Sheet '{selected_sheet}' ได้: {e}")
    st.stop()

st.title(f"📑 JVFS Device Claim System ({selected_sheet})")

# --- ส่วนที่ 1: Dashboard ---
if not df.empty and "แก้ในTrackMo" in df.columns:
    st.subheader(f"📊 ภาพรวมการเคลม - {selected_sheet}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายการทั้งหมด", len(df))
    track_series = df["แก้ในTrackMo"].fillna("").astype(str).str.strip()
    m2.metric("Pending", len(df[track_series == "Pending"]))
    m3.metric("In Progress", len(df[track_series == "inprogress"]))
    m4.metric("Done", len(df[track_series == "Done"]))
    st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล ---
with st.expander(f"➕ เพิ่มรายการใหม่ลงใน {selected_sheet}"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            branch = st.selectbox("สาขา", ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"])
            counter = st.text_input("Counter")
            sn_faulty = st.text_input("Serial เครื่องที่เสีย (บังคับ)")
            sn_to_center = st.text_input("Serial เครื่องที่ส่งให้ศูนย์")
        with col2:
            status = st.selectbox("แก้ในTrackMo", ["Pending", "inprogress", "Done"])
            date_claim = st.date_input("วันที่ส่งเคลม", value=None)
            date_install = st.date_input("วันที่นำไปติดตั้งใหม่", value=None)
            sn_new = st.text_input("Serial เครื่องที่เปลี่ยนใหม่")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not sn_faulty:
                st.warning("⚠️ กรุณากรอก Serial เครื่องที่เสีย")
            else:
                str_date_claim = date_claim.strftime("%Y-%m-%d") if date_claim else ""
                str_date_install = date_install.strftime("%Y-%m-%d") if date_install else ""
                
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง":
