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
ASSET_COLUMNS = ["Serial number","Location","วันที่ซื้อ"]

# 4. Sidebar
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()

# 5. ดึงข้อมูลจาก Tab ชื่อ "Wesgan"
try:
    df = conn.read(worksheet="Wesgan", ttl="0") # <--- เปลี่ยนตรงนี้เป็นชื่อ Tab ใหม่
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
        input_price = d2.text_input("PurchasePrice", value="0")

        if st.form_submit_button("💾 บันทึกข้อมูล"):
            if input_code:
                new_row = pd.DataFrame([{
                    "AssetCode": str(input_code),
                    "Serial": str(input_sn),
                    "ModelName": str(input_model),
                    "AssetTypeName": str(input_type),
                    "BrandName": str(input_brand),
                    "LocationName": str(input_loc),
                    "PurchaseDate": input_date.strftime("%Y-%m-%d"),
                    "PurchasePrice": str(input_price)
                }])
                
                df_updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                # บันทึกกลับไปที่ Tab "Wesgan"
                conn.update(worksheet="Wesgan", data=df_updated)
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
