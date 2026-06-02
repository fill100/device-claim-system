import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# แปลงโค้ดทั้งหมดให้เป็นฟังก์ชัน เพื่อรองรับการเรียกใช้งานร่วมกับ app.py ตัวใหม่
def show_asset_system(conn):
    st.markdown("### ระบบจัดการทรัพย์สิน (Asset System)")

    # --- 1. กำหนดโครงสร้างข้อมูล ---
    ASSET_COLUMNS = ["Serial Number (เลขซีเรียล)", "Model Name (ชื่อรุ่น)", "Location (สถานที่)", "วันที่ซื้อ"]

    # --- 2. ดึงข้อมูลจาก Google Sheets ---
    try:
        # บังคับดึงข้อมูลจาก Worksheet "Asset Management"
        df = conn.read(worksheet="Asset Management", ttl="0")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # ตรวจสอบคอลัมน์ให้ครบตามโครงสร้าง
            for col in ASSET_COLUMNS:
                if col not in df.columns: df[col] = ""
            df = df[ASSET_COLUMNS]
        else:
            df = pd.DataFrame(columns=ASSET_COLUMNS)
    except Exception:
        df = pd.DataFrame(columns=ASSET_COLUMNS)

    # --- 3. จัดการ State สำหรับการแก้ไข ---
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = None
    if "row_index" not in st.session_state:
        st.session_state.row_index = None

    def reset_edit_state():
        st.session_state.edit_data = None
        st.session_state.row_index = None

    # --- 4. ตัวกรองข้อมูลบนหน้าเว็บ (Model Filter) ---
    st.subheader("🎯 ตัวกรอง Model")
    # ป้องกันแอปพังกรณีฐานข้อมูลยังว่างเปล่า
    existing_models = sorted(df["Model Name (ชื่อรุ่น)"].dropna().unique().tolist()) if not df.empty else []
    all_models = ["ทั้งหมด"] + existing_models
    filter_model = st.selectbox("เลือกดูเฉพาะรุ่น:", all_models)

    # กรองข้อมูลเพื่อเอาไปแสดงผลบนตารางย่อย
    view_df = df.copy()
    if filter_model != "ทั้งหมด":
        view_df = view_df[view_df["Model Name (ชื่อรุ่น)"] == filter_model]

    # --- 5. UI หลัก (Form สำหรับเพิ่ม/แก้ไขข้อมูลหลัก) ---
    st.title("🛡️ Asset Management")

    is_editing = st.session_state.edit_data is not None
    expander_label = "📝 แก้ไขข้อมูลทรัพย์สิน" if is_editing else "➕ ลงทะเบียนทรัพย์สินใหม่"

    with st.expander(expander_label, expanded=is_editing):
        with st.form("asset_form", clear_on_submit=True):
            current_val = st.session_state.edit_data if is_editing else {}
            
            col1, col2 = st.columns(2)
            with col1:
                input_sn = st.text_input("Serial Number", value=current_val.get("Serial Number (เลขซีเรียล)", ""))
                input_model = st.text_input("Model Name", value=current_val.get("Model Name (ชื่อรุ่น)", ""))
            with col2:
                input_loc = st.text_input("Location", value=current_val.get("Location (สถานที่)", ""))
                
                try:
                    if is_editing and current_val.get("วันที่ซื้อ"):
                        default_date = datetime.strptime(current_val.get("วันที่ซื้อ"), "%d-%m-%Y")
                    else:
                        default_date = datetime.now()
                except Exception:
                    default_date = datetime.now()
                
                input_date = st.date_input("วันที่ซื้อ", value=default_date, format="DD/MM/YYYY")
            
            b_col1, b_col2 = st.columns([1, 5])
            with b_col1:
                submit = st.form_submit_button("💾 บันทึก")
            with b_col2:
                if is_editing:
                    if st.form_submit_button("❌ ยกเลิกการแก้ไข"):
                        reset_edit_state()
                        st.rerun()

            if submit:
                if input_sn.strip() != "":
                    updated_row_data = {
                        "Serial Number (เลขซีเรียล)": str(input_sn),
                        "Model Name (ชื่อรุ่น)": str(input_model),
                        "Location (สถานที่)": str(input_loc),
                        "วันที่ซื้อ": input_date.strftime("%d-%m-%Y"),
                    }
                    
                    try:
                        if is_editing:
                            df.iloc[st.session_state.row_index] = updated_row_data
                            success_msg = "อัปเดตข้อมูลเรียบร้อยแล้ว!"
                        else:
                            new_row_df
