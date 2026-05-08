import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. รายชื่อ Sheet ทั้งหมดที่มีในไฟล์ของคุณ (ตรวจสอบชื่อให้ตรงกับหน้าเว็บ Google Sheets)
AVAILABLE_SHEETS = ["Signature pad", "Passpost", "Iris Scaner","Printer Thermal (ปริ้นคิว)","Printer Pantum","Honeywell g1950","Newland HR2000","UPS ประจำศูนย์","Android Box","Adapter Android Box"
                   ,"Monitor","PC","CCTV","TV"] 

# 2. เพิ่มตัวเลือกใน Sidebar เพื่อเลือก Sheet ที่ต้องการทำงาน
st.sidebar.title("📁 การจัดการข้อมูล")
selected_sheet = st.sidebar.selectbox("เลือก Worksheet ที่ต้องการใช้งาน:", AVAILABLE_SHEETS)

# กำหนดชื่อคอลัมน์มาตรฐาน (ต้องมีเหมือนกันทุก Sheet)
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "แก้ในTrackMo"
]

# ดึงข้อมูลจาก Sheet ที่เลือก
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    
    if df is not None and not df.empty:
        # ล้างช่องว่างที่หัวคอลัมน์
        df.columns = df.columns.str.strip()
        
        # ตรวจสอบคอลัมน์ที่ขาดหายไป
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ Worksheet '{selected_sheet}' ขาดคอลัมน์: {', '.join(missing_cols)}")
            for col in missing_cols:
                df[col] = ""
    else:
        # ถ้า Sheet ว่าง ให้สร้าง DataFrame เปล่าที่มีหัวตารางครบ
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Sheet '{selected_sheet}' ได้: {e}")
    st.stop()

st.title(f"📑 JVFS Device Claim System ({selected_sheet})")

# --- ส่วนที่ 1: Dashboard สรุปผล ---
if not df.empty and "แก้ในTrackMo" in df.columns:
    st.subheader(f"📊 ภาพรวมการเคลม - {selected_sheet}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายการทั้งหมด", len(df))
    
    track_series = df["แก้ในTrackMo"].fillna("").astype(str).str.strip()
