import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Asset Management", layout="wide")

# ซ่อนเมนูเดิมเพื่อใช้ Sidebar ที่เราแต่งเอง
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 2. เชื่อมต่อ Google Sheets (ใช้ชื่อจาก Secrets)
try:
    conn = st.connection("gsheets_wesgan", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดตรวจสอบ Secrets และสิทธิ์ Editor")
    st.stop()

# 3. กำหนดหัวข้อคอลัมน์ทรัพย์สิน
ASSET_COLUMNS = [
    "AssetCode", "Serial", "ModelName", "AssetTypeName", 
    "BrandName", "LocationName", "PurchaseDate", "PurchasePrice"
]

# 4. Sidebar เมนูสลับหน้า
with st.sidebar:
    st.markdown("# 🎮 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()
    st.caption("v1.3.1 | Separate Database Mode")

# 5. ดึงข้อมูลจาก Sheet1
try:
    df = conn.read(worksheet="Sheet1", ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        # ตรวจสอบคอลัมน์ให้ครบ
        for col in ASSET_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[ASSET_COLUMNS]
    else:
        df = pd.DataFrame(columns=ASSET_COLUMNS)
except Exception:
    df = pd.DataFrame(columns=ASSET_COLUMNS)

# 6. UI หลัก
st.title("🛡️ Wesgan Asset Management")

# --- ส่วนลงทะเบียนใหม่ ---
with st.expander("➕ ลงทะเบียนทรัพย์สินใหม่"):
    with st.form("add_asset_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_code = st.text_input("AssetCode")
            a_sn = st.text_input("Serial Number")
        with c2:
            a_model = st.text_input("ModelName")
            a_type = st.text_input("AssetTypeName")
        with c3:
            a_brand = st.text_input("BrandName")
            a_loc = st.text_input("LocationName")
        
        d1, d2 = st.columns(2)
        p_date = d1.date_input("PurchaseDate")
        p_price = d2.text_input("PurchasePrice", value="0")

        if st.form_submit_button("💾 บันทึกข้อมูล"):
            if a_code:
                # แปลงข้อมูลทุกอย่างเป็น String เพื่อป้องกัน UnsupportedOperationError
                new_row = pd.DataFrame([{
                    "AssetCode": str(a_code),
                    "Serial": str(a_sn),
                    "ModelName": str(a_model),
                    "AssetTypeName": str(a_type),
                    "BrandName": str(a_brand),
                    "LocationName": str(a_loc),
                    "PurchaseDate": p_date.strftime("%Y-%m-%d"),
                    "PurchasePrice": str(a_price)
                }])
                
                # รวมข้อมูลและบันทึก
                df_updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet="Sheet1", data=df_updated)
                st.success(f"บันทึกรหัส {a_code} เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("กรุณาระบุ AssetCode")

# --- ตารางแสดงผลและค้นหา ---
st.divider()
search_q = st.text_input("🔍 ค้นหาทรัพย์สิน (พิมพ์ AssetCode, Serial, หรือสถานที่):")

view_df = df.copy()
if search_q:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)
