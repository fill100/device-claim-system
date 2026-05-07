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

# --- ฟังก์ชันบันทึกข้อมูล ---
with st.expander("➕ บันทึกการเคลมใหม่ (อ้างอิงตามไฟล์ JVFS)"):
    with st.form("claim_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            d_type = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขา", branches)
            counter = st.text_input("เคาน์เตอร์ / ชุดที่ / กล้องตัวที่")
            asset_no = st.text_input("Asset No.")
        with col2:
            sn_faulty = st.text_input("Serial Number (ตัวเสีย)")
            symptom = st.text_area("อาการเสีย")
            status = st.selectbox("สถานะ", ["inprogress", "Done", "Pending"])
            sn_new = st.text_input("Serial Number (ตัวใหม่)")
        
        trackmo = st.checkbox("อัปเดตใน TrackMo แล้ว")
        submit = st.form_submit_button("บันทึกข้อมูล")

        if submit:
            new_data = pd.DataFrame([{
                "วันที่แจ้ง": datetime.now().strftime("%Y-%m-%d"),
                "ประเภทอุปกรณ์": d_type,
                "สาขา": branch,
                "Counter": counter,
                "Asset No.": asset_no,
                "Serial เครื่องที่เสีย": sn_faulty,
                "อาการ": symptom,
                "สถานะ": status,
                "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                "แก้ในTrackMo": trackmo
            }])
            
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
            st.cache_data.clear()
            st.rerun()

# --- ฟังก์ชันค้นหาและจำแนกอุปกรณ์ ---
st.divider()
st.subheader("🔍 ค้นหาและดูรายงาน")

# Filter รายการ
c1, c2 = st.columns([1, 3])
with c1:
    search = st.text_input("🔎 ค้นหา S/N หรือ Asset No.")
    f_type = st.multiselect("จำแนกอุปกรณ์", device_types)
    f_status = st.multiselect("สถานะ", ["inprogress", "Done", "Pending"])

# กรองข้อมูล
filtered_df = df.copy()
if f_type:
    filtered_df = filtered_df[filtered_df["ประเภทอุปกรณ์"].isin(f_type)]
if f_status:
    filtered_df = filtered_df[filtered_df["สถานะ"].isin(f_status)]
if search:
    filtered_df = filtered_df[
        filtered_df["Serial เครื่องที่เสีย"].str.contains(search, na=False) | 
        filtered_df["Asset No."].str.contains(search, na=False)
    ]

# แสดงตาราง
st.dataframe(filtered_df, use_container_width=True)

# --- ฟังก์ชันดึง Report ---
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="📥 Download Report (Excel/CSV)",
        data=csv,
        file_name=f"JVFS_Report_{datetime.now().date()}.csv",
        mime="text/csv"
    )
