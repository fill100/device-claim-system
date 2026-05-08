import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. รายชื่อ Worksheet ทั้งหมด
AVAILABLE_SHEETS = [
    "Signature pad", 
    "Passpost", 
    "Iris Scaner",
    "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum",
    "Honeywell g1950",
    "Newland HR2000",
    "UPS ประจำศูนย์",
    "Android Box",
    "Adapter Android Box",
    "Monitor",
    "PC",
    "CCTV",
    "TV"
]

# 2. เมนูเลือก Worksheet ที่ Sidebar
st.sidebar.title("📁 ข้อมูลอุปกรณ์")
selected_sheet = st.sidebar.selectbox("เลือก Worksheet ที่ต้องการใช้งาน:", AVAILABLE_SHEETS)

# กำหนดชื่อคอลัมน์มาตรฐาน
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "แก้ในTrackMo"
]

# ดึงข้อมูลจาก Sheet ที่เลือก
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = ""
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

except Exception as e:
    st.error(f"❌ ไม่พบการตั้งค่า Spreadsheet หรือไฟล์มีปัญหา: {e}")
    st.stop()

st.title(f"📑 JVFS Device Claim System ({selected_sheet})")

# --- ส่วนที่ 1: Dashboard สรุปผล ---
st.subheader(f"📊 ภาพรวมการเคลม - {selected_sheet}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("รายการทั้งหมด", len(df))

if "แก้ในTrackMo" in df.columns:
    track_series = df["แก้ในTrackMo"].fillna("").astype(str).str.strip()
    m2.metric("Pending", len(df[track_series == "Pending"]))
    m3.metric("In Progress", len(df[track_series == "inprogress"]))
    m4.metric("Done", len(df[track_series == "Done"]))
st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูลใหม่ ---
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
                    "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "วันที่ส่งเคลม": str_date_claim,
                    "วันทีนำไปติดตั้งใหม่": str_date_install,
                    "สาขา": branch,
                    "counter": counter,
                    "Serial เครื่องที่เสีย": sn_faulty,
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_to_center,
                    "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                    "แก้ในTrackMo": status
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                updated_df = updated_df[EXPECTED_COLUMNS]
                
                conn.update(worksheet=selected_sheet, data=updated_df)
                st.success(f"✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ค้นหาและตรวจสอบข้อมูล ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")
search_col, refresh_col = st.columns([5, 1])

with search_col:
    search_query = st.text_input(
        "ค้นหา...",
        placeholder="S/N, Counter, หรือ สาขา",
        label_visibility="collapsed"
    )

with refresh_col:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# Logic การกรองข้อมูล
view_df = df.copy()
if search_query:
    mask = view_df.astype(str).apply(
        lambda x: x.str.contains(search_query, case=False, na=False)
    ).any(axis=1)
    view_df = view_df[mask]

# --- ส่วนที่ 4: แสดงผลตารางเดียวและระบบแก้ไข ---
if not view_df.empty:
    st.write(f"📊 พบข้อมูลทั้งหมด {len(view_df)} รายการ")
    # แสดงตารางเพียงครั้งเดียว
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    
    # ส่วนสำหรับแก้ไขข้อมูล (รวมอยู่ในเงื่อนไขเดียวกัน)
    with st.expander("📝 แก้ไขข้อมูลในแถวที่เลือก"):
        v_list = view_df["Serial เครื่องที่เสีย"].loc[view_df["Serial เครื่องที่เสีย"] != ""].unique().tolist()
        if v_list:
            sel_sn = st.selectbox("เลือก Serial ที่จะ
