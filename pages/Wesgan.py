import streamlit as st  # <--- ต้องมีบรรทัดนี้!
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# จากนั้นค่อยตามด้วยบรรทัดที่ 8 ที่เกิด Error
st.set_page_config(page_title="Asset Management", layout="wide")

# ซ่อนเมนูเดิม
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# ในไฟล์ Wesgan.py บรรทัดที่ 16-20 ควรเป็นแบบนี้:
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# 3. กำหนดหัวข้อคอลัมน์
ASSET_COLUMNS = ["Serial number","Location","Model Name (ชื่อรุ่น)","วันที่ซื้อ"]

# 4. Sidebar
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()

# 5. ดึงข้อมูลจาก Tab ชื่อ "Wesgan"
try:
    df = conn.read(worksheet="Asset Management", ttl="0") # <--- เปลี่ยนตรงนี้เป็นชื่อ Tab ใหม่
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        for col in ASSET_COLUMNS:
            if col not in df.columns: df[col] = ""
        df = df[ASSET_COLUMNS]
    else:
        df = pd.DataFrame(columns=ASSET_COLUMNS)
except:
    df = pd.DataFrame(columns=ASSET_COLUMNS)

# 6. UI หลัก
st.title("🛡️  Asset Management")

# --- ส่วนลงทะเบียนใหม่ (Serial, Model, Location, วันที่ซื้อ) ---
with st.expander("➕ ลงทะเบียนทรัพย์สินใหม่"):
    with st.form("add_asset_form", clear_on_submit=True):
        # 1. สร้างช่องกรอก 4 ช่อง
        col1, col2 = st.columns(2)
        with col1:
            input_sn = st.text_input("Serial Number (เลขซีเรียล)")
            input_model = st.text_input("Model Name (ชื่อรุ่น)")
        with col2:
            input_loc = st.text_input("Location (สถานที่)")
            input_date = st.date_input("วันที่ซื้อ", value=datetime.now())
        
        # ปุ่มบันทึก
        submit = st.form_submit_button("💾 บันทึกข้อมูล")

        if submit:
            # เช็คว่าอย่างน้อยต้องกรอก Serial Number
            if input_sn:
                # 2. จัดข้อมูลลง DataFrame (ใส่ให้ตรงกับคอลัมน์ใน Google Sheets)
                new_row = pd.DataFrame([{
                    "AssetCode": "",           # ปล่อยว่าง
                    "Serial": str(input_sn),
                    "ModelName": str(input_model), # เพิ่มตัวแปรนี้เข้าไปแล้วครับ
                    "AssetTypeName": "",       # ปล่อยว่าง
                    "BrandName": "",           # ปล่อยว่าง
                    "LocationName": str(input_loc),
                    "PurchaseDate": input_date.strftime("%Y-%m-%d"),
                    "PurchasePrice": ""        # ปล่อยว่าง
                }])
                
                # 3. บันทึกข้อมูล
                try:
                    # ตรวจสอบว่ามีตัวแปร df (ข้อมูลเก่า) อยู่แล้วก่อนเอามาต่อกัน
                    df_updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                    conn.update(worksheet="Wesgan", data=df_updated)
                    st.success(f"บันทึกข้อมูล {input_model} (S/N: {input_sn}) เรียบร้อยแล้ว!")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")
            else:
                st.error("กรุณาระบุ Serial Number ก่อนบันทึกครับ")

# --- ตารางแสดงผล ---
st.divider()
search = st.text_input("🔍 ค้นหา:")
view_df = df.copy()
if search:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)
