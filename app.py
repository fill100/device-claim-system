import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim", layout="wide")

# เชื่อมต่อ Google Sheets
# แก้ไข: เพิ่มสิทธิ์การเข้าถึงข้อมูลให้ชัดเจน
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูล (เพิ่ม Error Handling)
try:
    df = conn.read(ttl="0")
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
    st.info("ตรวจสอบว่าได้ตั้งค่า Secrets ใน Streamlit Cloud หรือยัง?")
    st.stop()
# ในที่นี้ขอยกตัวอย่างรายชื่อสาขาหลักๆ ตามไฟล์ที่คุณส่งมา
branch_list = ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "กรุงเทพมหานคร 5 (สจก.9)", 
    "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)", "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", 
    "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", 
    "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", 
    "จันทบุรี", "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร", 
    "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", 
    "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง", "ระนอง", 
    "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", 
    "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"]
device_types = [
    "Signature pad", "Monitor Dell", "UPS ประจำศูนย์", "CCTV", 
    "TV Samsung", "Printer Pantum", "Passport Scanner", 
    "Iris Scanner", "Android Box", "Newland HR2000"
]

st.title("📑 JVFS Device Claim System")

# --- ส่วนบันทึกและแก้ไข (Input & Edit) ---
with st.expander("➕ เพิ่มรายการเคลมใหม่"):
    with st.form("add_claim", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            d_type = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขา", branch_list)
            # ใช้ชื่อกลางว่า Counter เพื่อรองรับทั้ง "ชุดคิวที่" หรือ "กล้องตัวที่"
            counter = st.text_input("ชุดที่ / เคาน์เตอร์ / กล้องตัวที่")
        with c2:
            asset_no = st.text_input("Asset No.")
            sn_fault = st.text_input("Serial เครื่องที่เสีย")
            symptom = st.text_area("อาการเสีย")
        with c3:
            status = st.selectbox("สถานะ", ["Done", "inprogress", "Pending"])
            sn_new = st.text_input("Serial เครื่องที่เปลี่ยนใหม่")
            trackmo = st.checkbox("แก้ใน TrackMo แล้ว")

        if st.form_submit_button("บันทึกข้อมูล"):
            new_row = pd.DataFrame([{
                "วันที่แจ้ง": datetime.now().strftime("%Y-%m-%d"),
                "ประเภทอุปกรณ์": d_type,
                "สาขา": branch,
                "Counter": counter,
                "Asset No.": asset_no,
                "Serial เครื่องที่เสีย": sn_fault,
                "อาการ": symptom,
                "สถานะ": status,
                "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                "แก้ในTrackMo": trackmo
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("บันทึกสำเร็จ!")
            st.rerun()

# --- ส่วนการค้นหาและจำแนกอุปกรณ์ (Search & Categorize) ---
st.divider()
col_search, col_filter = st.columns([2, 1])

with col_search:
    search = st.text_input("🔎 ค้นหา S/N หรือ Asset No.")
with col_filter:
    type_filter = st.multiselect("จำแนกตามประเภท", device_types)

# กรองข้อมูล
display_df = df.copy()
if search:
    display_df = display_df[
        display_df["Serial เครื่องที่เสีย"].str.contains(search, na=False) | 
        display_df["Asset No."].str.contains(search, na=False)
    ]
if type_filter:
    display_df = display_df[display_df["ประเภทอุปกรณ์"].isin(type_filter)]

# แสดงผลตารางหลัก
st.subheader("📋 รายการข้อมูลทั้งหมด")
st.dataframe(display_df, use_container_width=True)

# --- ส่วนการดึง Report ---
if not display_df.empty:
    csv = display_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="📥 Download Report (CSV)",
        data=csv,
        file_name=f"JVFS_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
