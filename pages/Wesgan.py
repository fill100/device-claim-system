import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title=" Asset Management", layout="wide")

# ซ่อนเมนูเดิมของ Streamlit เพื่อใช้ Sidebar ที่เราแต่งเอง
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 2. เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. กำหนดหัวข้อคอลัมน์ตามที่คุณต้องการ
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

# 5. ดึงข้อมูลจาก Google Sheets
try:
    df_wesgan = conn.read(worksheet="Wesgan", ttl="0")
    if df_wesgan is None or df_wesgan.empty:
        df_wesgan = pd.DataFrame(columns=ASSET_COLUMNS)
    else:
        # ตรวจสอบว่ามีคอลัมน์ครบตามที่กำหนดไหม
        df_wesgan.columns = df_wesgan.columns.str.strip()
        for col in ASSET_COLUMNS:
            if col not in df_wesgan.columns:
                df_wesgan[col] = ""
        df_wesgan = df_wesgan[ASSET_COLUMNS]
except Exception:
    st.warning("⚠️ ไม่พบ Worksheet 'Wesgan' ระบบจะใช้โครงสร้างใหม่")
    df_wesgan = pd.DataFrame(columns=ASSET_COLUMNS)

# 6. ส่วนแสดงผลหลัก
st.title("🛡️ ระบบจัดการทรัพย์สินนอกระบบ (Wesgan)")

# --- ส่วนเพิ่มทรัพย์สินใหม่ ---
with st.expander("➕ ลงทะเบียนทรัพย์สินใหม่"):
    with st.form("add_asset_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_code = st.text_input("AssetCode (รหัสทรัพย์สิน)")
            a_sn = st.text_input("Serial Number")
            a_model = st.text_input("ModelName (ชื่อรุ่น)")
        with c2:
            a_type = st.text_input("AssetTypeName (ประเภท)")
            a_brand = st.text_input("BrandName (ยี่ห้อ)")
            a_loc = st.text_input("LocationName (สถานที่ติดตั้ง)")
        with c3:
            a_date = st.date_input("PurchaseDate (วันที่ซื้อ)", value=datetime.now())
            a_price = st.number_input("PurchasePrice (ราคาซื้อ)", min_value=0.0, step=100.0)
            
        if st.form_submit_button("บันทึกข้อมูลทรัพย์สิน"):
            if a_code and a_sn:
                new_asset = pd.DataFrame([{
                    "AssetCode": a_code,
                    "Serial": a_sn,
                    "ModelName": a_model,
                    "AssetTypeName": a_type,
                    "BrandName": a_brand,
                    "LocationName": a_loc,
                    "PurchaseDate": a_date.strftime("%Y-%m-%d"),
                    "PurchasePrice": str(a_price)
                }])
                df_updated = pd.concat([df_wesgan, new_asset], ignore_index=True).astype(str)
                conn.update(worksheet="Wesgan", data=df_updated)
                st.success(f"ลงทะเบียน {a_code} เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("กรุณากรอก AssetCode และ Serial เป็นอย่างน้อย")

# --- ส่วนแก้ไข/ลบรายการ ---
if not df_wesgan.empty:
    with st.expander("📝 แก้ไขข้อมูล หรือ ลบรายการ"):
        asset_list = df_wesgan["AssetCode"].tolist()
        sel_asset = st.selectbox("เลือก AssetCode ที่ต้องการจัดการ:", asset_list)
        idx = df_wesgan.index[df_wesgan["AssetCode"] == sel_asset].tolist()[0]
        row = df_wesgan.loc[idx]
        
        with st.form("edit_asset_form"):
            e1, e2 = st.columns(2)
            with e1:
                edit_loc = st.text_input("แก้ไข LocationName", value=str(row["LocationName"]))
                edit_price = st.text_input("แก้ไข PurchasePrice", value=str(row["PurchasePrice"]))
            with e2:
                edit_type = st.text_input("แก้ไข AssetTypeName", value=str(row["AssetTypeName"]))
                edit_brand = st.text_input("แก้ไข BrandName", value=str(row["BrandName"]))
            
            btn_up, btn_del = st.columns(2)
            if btn_up.form_submit_button("💾 อัปเดตข้อมูล"):
                df_wesgan.at[idx, "LocationName"] = edit_loc
                df_wesgan.at[idx, "PurchasePrice"] = edit_price
                df_wesgan.at[idx, "AssetTypeName"] = edit_type
                df_wesgan.at[idx, "BrandName"] = edit_brand
                conn.update(worksheet="Wesgan", data=df_wesgan.astype(str))
                st.success("อัปเดตข้อมูลแล้ว")
                st.rerun()
            
            if btn_del.form_submit_button("🗑️ ลบทรัพย์สินนี้"):
                df_dropped = df_wesgan.drop(idx)
                conn.update(worksheet="Wesgan", data=df_dropped.astype(str))
                st.warning(f"ลบ {sel_asset} ออกจากระบบแล้ว")
                st.rerun()

# --- ตารางแสดงรายการทั้งหมด ---
st.divider()
st.subheader("🔍 รายการทรัพย์สินทั้งหมด")
search_q = st.text_input("ค้นหาทรัพย์สิน (พิมพ์ AssetCode, Serial, หรือสถานที่):")

view_df = df_wesgan.copy()
if search_q:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

st.dataframe(view_df, use_container_width=True, hide_index=True)

# ปุ่ม Export CSV
if not view_df.empty:
    csv_data = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Asset Report (CSV)", csv_data, "wesgan_assets.csv", "text/csv")
