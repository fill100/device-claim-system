import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Wesgan Asset Management", layout="wide")

# ซ่อนเมนูเดิม
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# 2. เชื่อมต่อ Google Sheets
try:
    conn = st.connection("gsheets_wesgan", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ เชื่อมต่อไม่ได้: ตรวจสอบ Secrets (type='gsheets') และการแชร์สิทธิ์ Editor")
    st.stop()

# 3. กำหนดหัวข้อคอลัมน์
ASSET_COLUMNS = ["AssetCode", "Serial", "ModelName", "AssetTypeName", "BrandName", "LocationName", "PurchaseDate", "PurchasePrice"]

# 4. Sidebar
with st.sidebar:
    st.markdown("# 🎮 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()
    st.caption("v1.3.2 | Fix NameError")

# 5. ดึงข้อมูล
try:
    df = conn.read(worksheet="Sheet1", ttl="0")
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
st.title("🛡️ Wesgan Asset Management")

# --- ส่วนลงทะเบียนใหม่ ---
with st.expander("➕ ลงทะเบียนทรัพย์สินใหม่"):
    with st.form("add_asset_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            input_code = st.text_input("AssetCode")
            input_sn = st.text_input("Serial Number")
        with c2:
            input_model = st.text_input("ModelName")
            input_type = st.text_input("AssetTypeName")
        with c3:
            input_brand = st.text_input("BrandName")
            input_loc = st.text_input("LocationName")
        
        d1, d2 = st.columns(2)
        input_date = d1.date_input("PurchaseDate")
        input_price = d2.text_input("PurchasePrice", value="0") # รับค่าเป็น p_price

        if st.form_submit_button("💾 บันทึกข้อมูล"):
            if input_code:
                # แก้ไข NameError โดยการใช้ชื่อตัวแปรให้ตรงกันทั้งหมด
                new_row = pd.DataFrame([{
                    "AssetCode": str(input_code),
                    "Serial": str(input_sn),
                    "ModelName": str(input_model),
                    "AssetTypeName": str(input_type),
                    "BrandName": str(input_brand),
                    "LocationName": str(input_loc),
                    "PurchaseDate": input_date.strftime("%Y-%m-%d"),
                    "PurchasePrice": str(input_price) # ใช้ชื่อที่รับมาจาก text_input ด้านบน
                }])
                
                df_updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet="Sheet1", data=df_updated)
                st.success(f"บันทึกรหัส {input_code} สำเร็จ!")
                st.rerun()
            else:
                st.error("กรุณาระบุ AssetCode")

# --- ตารางแสดงผล ---
st.divider()
search = st.text_input("🔍 ค้นหา:")
view_df = df.copy()
if search:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)
