import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

# กำหนดชื่อคอลัมน์มาตรฐานที่ต้องมีในระบบ
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง","วันที่ส่งเคลม","วันทีนำไปติดตั้งใหม่","สาขา","counter","Serial เครื่องที่เสีย","Serial เครื่องที่ส่งให้ศูนย์","Serial เครื่องที่เปลี่ยนใหม่","แก้ในTrackMo"
]

# ดึงข้อมูลหลัก
try:
    df = conn.read(ttl="0")
    
    if df is not None and not df.empty:
        # ล้างช่องว่างหน้า-หลังชื่อคอลัมน์ ป้องกัน KeyError
        df.columns = df.columns.str.strip()
        
        # กรณี Sheet ว่างเปล่า ให้สร้าง DataFrame เปล่าที่มีหัวตารางครบ
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

except Exception as e:
    st.error(f"❌ ไม่พบการตั้งค่า Spreadsheet หรือไฟล์มีปัญหา: {e}")
    st.stop()

# ข้อมูลสำหรับ Dropdown
branches = ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"]
device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Monitor Dell", "Dell Pro Tower", "CCTV", "TV Samsung"
]

st.title("📑 JVFS Device Claim System")

# --- ส่วนที่ 1: Dashboard สรุปผล ---
# เช็คก่อนว่ามีคอลัมน์ 'สถานะ' ไหมก่อนรันสรุป
if not df.empty and "สถานะ" in df.columns:
    st.subheader("📊 ภาพรวมการเคลม")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายการทั้งหมด", len(df))
    # ใช้ .get() หรือเช็คค่าเพื่อป้องกัน Error กรณีข้อมูลในแถวเป็นค่าว่าง
    m2.metric("รอดำเนินการ (Pending)", len(df[df["สถานะ"].str.strip() == "Pending"] if not df.empty else []))
    m3.metric("กำลังทำ (In Progress)", len(df[df["สถานะ"].str.strip() == "inprogress"] if not df.empty else []))
    m4.metric("เสร็จสิ้น (Done)", len(df[df["สถานะ"].str.strip() == "Done"] if not df.empty else []))
    st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล ---
with st.expander("➕ เพิ่มรายการเคลมใหม่"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขา", branches)
            asset_no = st.text_input("Asset No.")
            sn_faulty = st.text_input("S/N เครื่องที่เสีย")
        with col2:
            status = st.selectbox("สถานะ", ["Pending", "inprogress", "Done"])
            symptom = st.text_area("อาการเสีย")
            sn_new = st.text_input("S/N เครื่องใหม่ (ถ้ามี)")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not asset_no or not sn_faulty:
                st.warning("⚠️ กรุณากรอก Asset No. และ S/N เครื่องเสีย")
            else:
                new_row = pd.DataFrame([{
                    "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "ประเภทอุปกรณ์": category,
                    "สาขา": branch,
                    "Asset No.": asset_no,
                    "S/N เครื่องเสีย": sn_faulty,
                    "อาการเสีย": symptom,
                    "สถานะ": status,
                    "S/N เครื่องใหม่": sn_new
                }])
                # คลีนข้อมูลก่อนรวม
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ระบบค้นหาและตัวกรอง ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")
search_col1, search_col2 = st.columns([2, 1])

with search_col1:
    search_query = st.text_input("🔎 ค้นหาจาก S/N, Asset No, หรือชื่อสาขา", placeholder="พิมพ์คำค้นหา...")

with search_col2:
    options = ["ทั้งหมด"]
    if "ประเภทอุปกรณ์" in df.columns:
        options += sorted(df["ประเภทอุปกรณ์"].unique().tolist())
    filter_cat = st.selectbox("🏷️ เลือกประเภทอุปกรณ์", options)

# Logic การกรองข้อมูล
view_df = df.copy()
if filter_cat != "ทั้งหมด":
    view_df = view_df[view_df["ประเภทอุปกรณ์"] == filter_cat]

if search_query:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

# --- ส่วนที่ 4: แสดงผลและแก้ไขข้อมูล ---
if not view_df.empty:
    st.write(f"พบข้อมูล {len(view_df)} รายการ")
    st.dataframe(view_df, use_container_width=True, hide_index=True)

    with st.expander("📝 แก้ไขสถานะหรือข้อมูลเครื่องใหม่"):
        # ป้องกันกรณี S/N ซ้ำหรือว่าง
        valid_sn_list = view_df["S/N เครื่องเสีย"].dropna().unique().tolist()
        selected_sn = st.selectbox("เลือก S/N ที่ต้องการแก้ไข", valid_sn_list)
        
        if selected_sn:
            # ดึงข้อมูลแถวที่จะแก้
            target_data = df[df["S/N เครื่องเสีย"] == selected_sn].iloc[0]
            
            with st.form("edit_form"):
                edit_col1, edit_col2 = st.columns(2)
                with edit_col1:
                    # พยายามหา Index ของสถานะเดิม ถ้าหาไม่เจอให้เริ่มที่ 0
                    current_status = target_data["สถานะ"]
                    status_options = ["Pending", "inprogress", "Done"]
                    try:
                        status_idx = status_options.index(current_status)
                    except:
                        status_idx = 0
                        
                    new_status = st.selectbox("อัปเดตสถานะ", status_options, index=status_idx)
                with edit_col2:
                    new_sn_new = st.text_input("อัปเดต S/N เครื่องใหม่", value=str(target_data["S/N เครื่องใหม่"]))
                
                if st.form_submit_button("ยืนยันการแก้ไข"):
                    idx = df.index[df["S/N เครื่องเสีย"] == selected_sn].tolist()[0]
                    df.at[idx, "สถานะ"] = new_status
                    df.at[idx, "S/N เครื่องใหม่"] = new_sn_new
                    
                    conn.update(data=df)
                    st.success(f"อัปเดต S/N {selected_sn} เรียบร้อย!")
                    st.rerun()

    # ปุ่มดาวน์โหลด
    csv = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลด CSV", csv, "claim_report.csv", "text/csv")
else:
    st.info("💡 ไม่พบข้อมูลที่ตรงตามเงื่อนไข")
