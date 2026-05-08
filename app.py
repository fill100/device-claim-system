import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

AVAILABLE_SHEETS = [
    "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

# Sidebar
st.sidebar.markdown("### 📁 เมนูจัดการอุปกรณ์")
selected_sheet = st.sidebar.selectbox("เลือกประเภทอุปกรณ์:", AVAILABLE_SHEETS)

EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่"
]

# ดึงข้อมูล
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
    st.error(f"❌ Error: {e}")
    st.stop()

# --- ปรับปรุง UI Header ---
st.markdown(f"## 📑 {selected_sheet} Management System")
st.markdown("---")

# --- ส่วนที่ 1: Dashboard (เหลือเฉพาะยอดรวม) ---
st.markdown("### 📊 ภาพรวมข้อมูล")
c1, c2 = st.columns([1, 3])
with c1:
    st.metric("📦 รายการทั้งหมด", len(df))

st.markdown("<br>", unsafe_allow_html=True)

    # แสดงผลแบบ Card สี
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 รายการทั้งหมด", total)
    c2.markdown(f"<div style='border-radius:5px; background-color:#ff4b4b; padding:10px; color:white;'><b>🔴 Pending: {pending}</b></div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='border-radius:5px; background-color:#fca311; padding:10px; color:white;'><b>🟠 In Progress: {inprogress}</b></div>", unsafe_allow_html=True)
    c4.markdown(f"<div style='border-radius:5px; background-color:#2b9348; padding:10px; color:white;'><b>🟢 Done: {done}</b></div>", unsafe_allow_html=True)
else:
    st.warning("ไม่พบคอลัมน์ 'แก้ในTrackMo'")

st.markdown("<br>", unsafe_allow_html=True)

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล (ปรับปรุงให้สะอาดตาขึ้น) ---
with st.expander("➕ เพิ่มข้อมูลการเคลมใหม่"):
    with st.form("main_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            branch = st.selectbox("เลือกสาขา", ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"])
            counter = st.text_input("Counter Number")
            sn_faulty = st.text_input("S/N เครื่องเสีย *")
        with f2:
            status = st.selectbox("สถานะการดำเนินการ", ["Pending", "inprogress", "Done"])
            sn_to_center = st.text_input("S/N ส่งศูนย์")
            sn_new = st.text_input("S/N เครื่องใหม่")
            
        if st.form_submit_button("💾 บันทึกข้อมูลลงในระบบ"):
            if not sn_faulty:
                st.error("กรุณาระบุ Serial เครื่องเสีย")
            else:
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "สาขา": branch, "counter": counter, "Serial เครื่องที่เสีย": sn_faulty,
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_to_center, "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                    "แก้ในTrackMo": status
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)[EXPECTED_COLUMNS]
                conn.update(worksheet=selected_sheet, data=updated_df)
                st.success("บันทึกข้อมูลสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ระบบค้นหาและตาราง ---
st.markdown("### 🔍 ตรวจสอบและแก้ไขข้อมูล")
s_col, r_col = st.columns([4, 1])
with s_col:
    q = st.text_input("ค้นหาด่วน:", placeholder="พิมพ์ Serial, สาขา หรือ Counter...")
with r_col:
    if st.button("🔄 ดึงข้อมูลล่าสุด"):
        st.cache_data.clear()
        st.rerun()

view_df = df.copy()
if q:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

# แสดงตารางด้วยสไตล์ที่อ่านง่าย
st.dataframe(view_df, use_container_width=True, hide_index=True)

# ส่วนแก้ไข
if not view_df.empty:
    with st.expander("📝 คลิกเพื่ออัปเดตสถานะ/แก้ไขข้อมูล"):
        sn_list = view_df["Serial เครื่องที่เสีย"].loc[view_df["Serial เครื่องที่เสีย"] != ""].unique().tolist()
        if sn_list:
            target_sn = st.selectbox("เลือกเครื่องที่ต้องการอัปเดต:", sn_list)
            row_data = df[df["Serial เครื่องที่เสีย"] == target_sn].iloc[0]
            
            with st.form("quick_edit"):
                e1, e2 = st.columns(2)
                with e1:
                    up_status = st.selectbox("อัปเดตสถานะใหม่", ["Pending", "inprogress", "Done"])
                with e2:
                    up_sn_new = st.text_input("อัปเดต S/N เครื่องใหม่", value=str(row_data["Serial เครื่องที่เปลี่ยนใหม่"]))
                
                if st.form_submit_button("✅ ยืนยันการอัปเดต"):
                    idx = df.index[df["Serial เครื่องที่เสีย"] == target_sn].tolist()[0]
                    df.at[idx, "แก้ในTrackMo"] = up_status
                    df.at[idx, "Serial เครื่องที่เปลี่ยนใหม่"] = up_sn_new
                    conn.update(worksheet=selected_sheet, data=df)
                    st.success("อัปเดตข้อมูลแล้ว!")
                    st.rerun()
