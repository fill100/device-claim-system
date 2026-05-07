import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลจากไฟล์ 'ศูนย์บริการ.csv' (สมมติว่าคุณเอาข้อมูลสาขาใส่ไว้ในอีก Sheet หนึ่ง)
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
device_categories = ["Signature pad", "Monitor Dell", "UPS", "CCTV", "TV Samsung", "Printer Pantum", "Passport Scanner", "Iris Scanner"]

st.title("📑 ระบบจัดการข้อมูลการเคลมอุปกรณ์ (JVFS)")

# --- ส่วนที่ 1: บันทึกและแก้ไขข้อมูล ---
with st.expander("➕ บันทึกรายการเคลมใหม่"):
    with st.form("add_claim"):
        col1, col2, col3 = st.columns(3)
        with col1:
            d_type = st.selectbox("ประเภทอุปกรณ์", device_categories)
            branch = st.selectbox("สาขา", branch_list)
            counter = st.text_input("เคาน์เตอร์ / ชุดที่")
        with col2:
            asset_no = st.text_input("Asset No.")
            sn_faulty = st.text_input("Serial Number (เครื่องเสีย)")
            symptom = st.text_area("อาการเสีย")
        with col3:
            status = st.selectbox("สถานะ", ["In Progress", "Done", "Pending"])
            sn_new = st.text_input("Serial Number (เครื่องใหม่/เปลี่ยน)")
            trackmo = st.checkbox("แก้ไขใน TrackMo แล้ว")
        
        submit = st.form_submit_button("บันทึกข้อมูล")
        
        if submit:
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "DeviceType": d_type,
                "Branch": branch,
                "Counter": counter,
                "AssetNo": asset_no,
                "SerialFaulty": sn_faulty,
                "Symptom": symptom,
                "Status": status,
                "SerialReplacement": sn_new,
                "TrackMoUpdated": trackmo,
                "ReinstallDate": ""
            }])
            # อ่านข้อมูลเก่ามาต่อกับข้อมูลใหม่แล้วอัปเดตกลับไปที่ Google Sheets
            existing_data = conn.read()
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success("บันทึกข้อมูลสำเร็จ!")

# --- ส่วนที่ 2: ค้นหาและจำแนกอุปกรณ์ ---
st.divider()
st.subheader("🔍 ค้นหาและรายงาน")

# โหลดข้อมูลปัจจุบัน
df = conn.read(ttl="0") # ดึงสดจาก Google Sheets

# ตัวกรอง (Filter)
c1, c2, c3 = st.columns(3)
with c1:
    search_term = st.text_input("ค้นหาจาก S/N หรือ Asset No.")
with c2:
    filter_device = st.multiselect("จำแนกตามประเภทอุปกรณ์", device_categories, default=device_categories)
with c3:
    filter_status = st.multiselect("สถานะ", ["In Progress", "Done", "Pending"], default=["In Progress", "Done", "Pending"])

# กรองข้อมูลตามเงื่อนไข
filtered_df = df[df["DeviceType"].isin(filter_device) & df["Status"].isin(filter_status)]
if search_term:
    filtered_df = filtered_df[filtered_df["SerialFaulty"].str.contains(search_term, na=False) | 
                              filtered_df["AssetNo"].str.contains(search_term, na=False)]

# แสดงผลตาราง
st.dataframe(filtered_df, use_container_width=True)

# --- ส่วนที่ 3: สรุปผลและดึง Report ---
st.divider()
col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    st.write("📊 **สรุปจำนวนเครื่องเสียแยกตามประเภท**")
    st.bar_chart(filtered_df["DeviceType"].value_counts())

with col_stat2:
    st.write("📥 **Export ข้อมูล**")
    csv = filtered_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="Download Report as CSV",
        data=csv,
        file_name=f"JVFS_Claim_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
