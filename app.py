import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# 1. เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลหลัก (ตารางสะสมรายการเคลม)
try:
    df = conn.read(ttl="0")
except Exception:
    st.error("❌ ไม่พบการตั้งค่า Spreadsheet! กรุณาตรวจสอบ 'Spreadsheet URL' ใน Streamlit Secrets")
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
# 3. ประเภทอุปกรณ์ (อ้างอิงจากไฟล์ที่คุณอัปโหลด)
device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor Dell", "Dell Pro Tower", "CCTV", "TV Samsung"
]

st.title("📑 JVFS Device Claim System")
st.info("ระบบบันทึกและติดตามสถานะการเคลมอุปกรณ์ (อัปเดตตามโครงสร้าง JVFS-DeviceClaim)")

# --- ส่วนที่ 1: บันทึกข้อมูลใหม่ ---
with st.expander("➕ เพิ่มรายการเคลมใหม่ (Add New Claim)"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขา", branches)
            counter = st.text_input("ชุดคิว / เคาน์เตอร์ / กล้องตัวที่")
        
        with col2:
            asset_no = st.text_input("Asset No.")
            sn_faulty = st.text_input("Serial เครื่องที่เสีย (S/N)")
            symptom = st.text_area("อาการเสีย / ปัญหาที่พบ")
            
        with col3:
            status = st.selectbox("สถานะ", ["Pending", "inprogress", "Done"])
            date_sent = st.date_input("วันที่ส่งเคลม", value=datetime.now())
            sn_new = st.text_input("Serial เครื่องที่เปลี่ยนใหม่")

        trackmo = st.checkbox("แก้ไขใน TrackMo เรียบร้อยแล้ว")
        remark = st.text_input("หมายเหตุเพิ่มเติม")

        if st.form_submit_button("บันทึกข้อมูลลงระบบ"):
            new_row = pd.DataFrame([{
                "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "วันที่ส่งเคลม": date_sent.strftime("%Y-%m-%d"),
                "ประเภทอุปกรณ์": category,
                "สาขา": branch,
                "ตำแหน่ง/เคาน์เตอร์": counter,
                "Asset No.": asset_no,
                "S/N เครื่องเสีย": sn_faulty,
                "อาการเสีย": symptom,
                "สถานะ": status,
                "S/N เครื่องใหม่": sn_new,
                "TrackMo": "Yes" if trackmo else "No",
                "หมายเหตุ": remark
            }])
            
            # อัปเดตไปยัง Google Sheets
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
            st.rerun()

# --- ส่วนที่ 2: แสดงข้อมูลและตัวกรอง ---
st.divider()
st.subheader("🔍 รายการอุปกรณ์ทั้งหมด")

# ตัวกรองข้อมูล
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    search_sn = st.text_input("🔎 ค้นหาจาก S/N หรือ Asset No.")
with f_col2:
    filter_cat = st.multiselect("กรองประเภทอุปกรณ์", device_types)
with f_col3:
    filter_stat = st.multiselect("กรองสถานะ", ["Pending", "inprogress", "Done"])

# การกรอง Dataframe
view_df = df.copy()
if search_sn:
    view_df = view_df[view_df['S/N เครื่องเสีย'].astype(str).str.contains(search_sn) | 
                      view_df['Asset No.'].astype(str).str.contains(search_sn)]
if filter_cat:
    view_df = view_df[view_df['ประเภทอุปกรณ์'].isin(filter_cat)]
if filter_stat:
    view_df = view_df[view_df['สถานะ'].isin(filter_stat)]

st.dataframe(view_df, use_container_width=True)

# ปุ่มดาวน์โหลด Report
if not view_df.empty:
    csv = view_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button("📥 ดาวน์โหลดรายงานเป็น CSV", csv, "JVFS_Claim_Report.csv", "text/csv")
