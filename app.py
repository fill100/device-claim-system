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
    st.error("❌ ไม่พบการตั้งค่า Spreadsheet! กรุณาตรวจสอบลิงก์ใน Secrets")
    st.stop()

# ข้อมูลสำหรับ Dropdown (อ้างอิงตามไฟล์ที่คุณอัปโหลด)
branches = ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"] # ปรับเพิ่มตามจริง
device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Monitor Dell", "Dell Pro Tower", "CCTV", "TV Samsung"
]

st.title("📑 JVFS Device Claim System")

# --- ส่วนที่ 1: ฟอร์มบันทึกข้อมูล (ด้านบน) ---
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
            # โครงสร้าง Data ที่จะเพิ่มลง Sheets
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
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ บันทึกสำเร็จ!")
            st.rerun()

st.divider()

# --- ส่วนที่ 2: ระบบค้นหาและเลือกประเภทอุปกรณ์ (ส่วนที่คุณต้องการเพิ่ม) ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")

# สร้างแถวสำหรับค้นหา
search_col1, search_col2 = st.columns([2, 1])

with search_col1:
    # ช่องพิมพ์ค้นหาอิสระ
    search_query = st.text_input("🔎 ค้นหาจาก S/N, Asset No, หรือชื่อสาขา", placeholder="พิมพ์เพื่อค้นหา...")

with search_col2:
    # ตัวกรองประเภทอุปกรณ์ (ดึงจากข้อมูลที่มีอยู่จริงในตาราง)
    if not df.empty and "ประเภทอุปกรณ์" in df.columns:
        options = ["ทั้งหมด"] + sorted(df["ประเภทอุปกรณ์"].unique().tolist())
    else:
        options = ["ทั้งหมด"]
    
    filter_cat = st.selectbox("🏷️ เลือกประเภทอุปกรณ์", options)

# --- ส่วนการกรองข้อมูล (Logic) ---
view_df = df.copy()

# 1. กรองตามประเภทอุปกรณ์ที่เลือก
if filter_cat != "ทั้งหมด":
    view_df = view_df[view_df["ประเภทอุปกรณ์"] == filter_cat]

# 2. กรองตามคำค้นหาที่พิมพ์
if search_query:
    # ค้นหาคำในทุกคอลัมน์ (Case-insensitive)
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

# --- แสดงผลตาราง ---
if not view_df.empty:
    st.write(f"พบข้อมูลทั้งหมด {len(view_df)} รายการ")
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    
    # ปุ่มดาวน์โหลดผลลัพธ์ที่กรองแล้ว
    csv = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลดรายการนี้ (CSV)", csv, "claim_report.csv", "text/csv")
else:
    st.info("ไม่พบข้อมูลที่ตรงตามเงื่อนไข")
