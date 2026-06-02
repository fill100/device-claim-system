import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเพจย่อย (จะแสดงผลแบบเต็มหน้าจอ)
st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

st.title("📑 JVFS Device Claim System")
st.caption("ระบบบันทึก ตรวจสอบ และติดตามสถานะการเคลมอุปกรณ์ไอทีประจำศูนย์บริการ")

# ฟังก์ชันเชื่อมต่อฐานข้อมูล Google Sheets
def get_sheets_connection():
    if "connections" not in st.secrets:
        st.error("❌ ไม่พบโครงสร้าง Secrets กรุณาตั้งค่า Spreadsheet URL ก่อนครับ")
        st.stop()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception:
        st.error("❌ ไม่สามารถเชื่อมต่อกับ Google Sheets ได้")
        st.stop()

# ข้อมูลดิบพื้นฐาน
branches_list = [
    "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", 
    "กรุงเทพมหานคร 5 (สจก.9)", "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)",
    "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม",
    "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", "สระบุรี", "สุพรรณบุรี",
    "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", "จันทบุรี",
    "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร",
    "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี",
    "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง",
    "ระนอง", "สงขลา", "สุราษฎร์ธานี", "กระบี่"
]

device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

# ดึงข้อมูลจาก Sheets
conn = get_sheets_connection()
df = conn.read(ttl="0")

# ฟอร์มบันทึกข้อมูลเคลม
with st.expander("➕ เพิ่มรายการเคลมใหม่", expanded=False):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขาที่พบปัญหา", branches_list)
            asset_no = st.text_input("Asset No.")
            sn_faulty = st.text_input("S/N เครื่องที่เสีย")
        with col2:
            status = st.selectbox("สถานะปัจจุบัน", ["Pending", "inprogress", "Done"])
            symptom = st.text_area("อาการเสียโดยละเอียด")
            sn_new = st.text_input("S/N เครื่องใหม่ / ของเปลี่ยนทดแทน")
        
        if st.form_submit_button("💾 บันทึกข้อมูลลง Google Sheets"):
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
            st.success("✅ อัปเดตข้อมูลเข้าฐานข้อมูลเรียบร้อยแล้ว!")
            st.rerun()

st.divider()

# ระบบกรองและค้นหาข้อมูล
st.subheader("🔍 ค้นหาและคัดกรองข้อมูล")
search_col1, search_col2 = st.columns([2, 1])
with search_col1:
    search_query = st.text_input("🔎 พิมพ์คำค้นหา...", placeholder="พิมพ์คำเพื่อค้นหาในตาราง...")
with search_col2:
    options = ["ทั้งหมด"] + sorted(df["ประเภทอุปกรณ์"].unique().tolist()) if not df.empty else ["ทั้งหมด"]
    filter_cat = st.selectbox("🏷️ เลือกเฉพาะอุปกรณ์", options)

view_df = df.copy()
if filter_cat != "ทั้งหมด":
    view_df = view_df[view_df["ประเภทอุปกรณ์"] == filter_cat]
if search_query:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

if not view_df.empty:
    st.write(f"📊 พบผลลัพธ์ข้อมูลทั้งหมด {len(view_df)} รายการ")
    st.dataframe(view_df, use_container_width=True, hide_index=True)
else:
    st.info("💡 ไม่พบข้อมูลตามเงื่อนไข")
