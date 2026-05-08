import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. รายชื่อ Worksheet
AVAILABLE_SHEETS = [
    "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

# Sidebar
st.sidebar.markdown("### 📁 เมนูจัดการข้อมูล")
selected_sheet = st.sidebar.selectbox("เลือก Worksheet:", AVAILABLE_SHEETS)

# 2. กำหนดคอลัมน์มาตรฐาน
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "สถานะ"
]

# ดึงข้อมูล
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        # ย้ายชื่อคอลัมน์ถ้าเป็นแบบเก่า
        if "แก้ในTrackMo" in df.columns:
            df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[EXPECTED_COLUMNS]
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.stop()

st.title(f"📑 JVFS Device Claim System ({selected_sheet})")

# --- ส่วนที่ 1: Dashboard UI (ปรับสีตามคำขอ) ---
st.subheader(f"📊 ภาพรวมการเคลม")

status_series = df["สถานะ"].fillna("").astype(str).str.strip().str.lower()

total = len(df)
pending = len(df[status_series == "pending"])
inprogress = len(df[status_series == "inprogress"])
done = len(df[status_series == "done"])

# ใช้ HTML/CSS เพื่อกำหนดสีเป๊ะๆ ตามที่คุณต้องการ
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("รายการทั้งหมด", total)

with c2:
    st.markdown(f"""
        <div style="background-color: #ff4b4b; padding: 15px; border-radius: 10px; text-align: center; color: white;">
            <small>Pending</small><br><span style="font-size: 24px; font-weight: bold;">{pending}</span>
        </div>
    """, unsafe_allow_html=True)

with c3:
    # 🟡 In Progress (สีเหลือง/ส้ม)
    st.markdown(f"""
        <div style="background-color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; color: black;">
            <small>In Progress</small><br><span style="font-size: 24px; font-weight: bold;">{inprogress}</span>
        </div>
    """, unsafe_allow_html=True)

with c4:
    # 🟢 Done (สีเขียว)
    st.markdown(f"""
        <div style="background-color: #28a745; padding: 15px; border-radius: 10px; text-align: center; color: white;">
            <small>Done</small><br><span style="font-size: 24px; font-weight: bold;">{done}</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล ---
with st.expander(f"➕ เพิ่มรายการใหม่"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            branch = st.selectbox("สาขา", ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"])
            counter = st.text_input("Counter")
            sn_faulty = st.text_input("Serial เครื่องที่เสีย (บังคับ)")
        with col2:
            status = st.selectbox("สถานะ", ["Pending", "inprogress", "Done"])
            date_claim = st.date_input("วันที่ส่งเคลม", value=None)
            sn_new = st.text_input("Serial เครื่องที่เปลี่ยนใหม่")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not sn_faulty:
                st.warning("⚠️ กรุณากรอก Serial เครื่องที่เสีย")
            else:
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "วันที่ส่งเคลม": date_claim.strftime("%Y-%m-%d") if date_claim else "",
                    "สาขา": branch, "counter": counter, "Serial เครื่องที่เสีย": sn_faulty,
                    "Serial เครื่องที่ส่งให้ศูนย์": "", "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                    "สถานะ": status
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)[EXPECTED_COLUMNS]
                conn.update(worksheet=selected_sheet, data=updated_df)
                st.success("✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ระบบค้นหาด่วน (พร้อมปุ่ม Refresh) ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")
sc1, sc2 = st.columns([5, 1])
with sc1:
    search_query = st.text_input("ค้นหาด่วน:", placeholder="Serial, สาขา...", label_visibility="collapsed")
with sc2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

view_df = df.copy()
if search_query:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)

# --- ส่วนที่ 4: ระบบแก้ไขสถานะ ---
if not view_df.empty:
    with st.expander("📝 แก้ไขสถานะ / อัปเดตข้อมูล"):
        sn_list = view_df["Serial เครื่องที่เสีย"].loc[view_df["Serial เครื่องที่เสีย"] != ""].unique().tolist()
        if sn_list:
            sel_sn = st.selectbox("เลือก Serial ที่จะแก้ไข", sn_list)
            target_data = df[df["Serial เครื่องที่เสีย"] == sel_sn].iloc[0]
            
            with st.form("edit_form"):
                e1, e2 = st.columns(2)
                with e1:
                    current_st = str(target_data["สถานะ"]).strip()
                    st_options = ["Pending", "inprogress", "Done"]
                    def_idx = st_options.index(current_st) if current_st in st_options else 0
                    new_status = st.selectbox("เปลี่ยนสถานะ", st_options, index=def_idx)
                with e2:
                    new_sn_center = st.text_input("Serial ส่งศูนย์", value=str(target_data["Serial เครื่องที่ส่งให้ศูนย์"]))
                    new_sn_new = st.text_input("Serial เครื่องใหม่", value=str(target_data["Serial เครื่องที่เปลี่ยนใหม่"]))
                
                if st.form_submit_button("ยืนยันการแก้ไข"):
                    idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
                    df.at[idx, "สถานะ"] = new_status
                    df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_center
                    df.at[idx, "Serial เครื่องที่เปลี่ยนใหม่"] = new_sn_new
                    conn.update(worksheet=selected_sheet, data=df)
                    st.success("อัปเดตเรียบร้อย!")
                    st.rerun()
