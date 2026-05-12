import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรกๆ)
st.set_page_config(page_title="Wesgan Asset Management", layout="wide")

# ซ่อนเมนูเดิมเพื่อความสวยงาม
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 2. เชื่อมต่อ Google Sheets ไฟล์ที่ 2
try:
    conn = st.connection("gsheets_wesgan", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูล Wesgan ได้ โปรดเช็ค Secrets")
    st.stop()

# 3. กำหนดหัวข้อคอลัมน์ (Asset System)
ASSET_COLUMNS = [
    "AssetCode", "Serial", "ModelName", "AssetTypeName", 
    "BrandName", "LocationName", "PurchaseDate", "PurchasePrice"
]

# 4. Sidebar Custom Navigation
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()
    st.caption("v1.3.0 | Wesgan Database")

# 5. ดึงข้อมูล
try:
    # อ่านจาก Sheet1 ของไฟล์ใหม่
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
st.title("🛡️ ระบบจัดการทรัพย์สินนอกระบบ (Wesgan)")

# --- ส่วนเพิ่มข้อมูล ---
with st.expander("➕ ลงทะเบียนทรัพย์สินใหม่"):
    with st.form("add_asset"):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_code = st.text_input("AssetCode")
            a_sn = st.text_input("Serial")
        with c2:
            a_model = st.text_input("ModelName")
            a_type = st.text_input("AssetTypeName")
        with c3:
            a_brand = st.text_input("BrandName")
            a_loc = st.text_input("LocationName")
        
        d1, d2 = st.columns(2)
        p_date = d1.date_input("PurchaseDate")
        p_price = d2.text_input("PurchasePrice", value="0")

        if st.form_submit_button("💾 บันทึกทรัพย์สิน"):
            if a_code:
                new_row = pd.DataFrame([{
                    "AssetCode": a_code, "Serial": a_sn, "ModelName": a_model,
                    "AssetTypeName": a_type, "BrandName": a_brand, "LocationName": a_loc,
                    "PurchaseDate": p_date.strftime("%Y-%m-%d"), "PurchasePrice": p_price
                }])
                df_updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet="Sheet1", data=df_updated)
                st.success("บันทึกสำเร็จ!")
                st.rerun()
            else: st.error("กรุณาระบุ AssetCode")

# --- ตารางแสดงผลและค้นหา ---
st.divider()
search = st.text_input("🔍 ค้นหาทรัพย์สิน:")
view_df = df.copy()
if search:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)

# ปุ่มดาวน์โหลด
if not view_df.empty:
    st.download_button("📥 Export CSV", view_df.to_csv(index=False).encode('utf-8-sig'), "wesgan_assets.csv")
