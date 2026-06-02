import streamlit as st
import pandas as pd
from datetime import datetime

# ใช้ฟังก์ชันที่รับ conn เข้ามาโดยตรงจาก app.py
def run_transfer_page(conn):
    st.title("✈️ Transfer Management System")
    st.subheader("ระบบโอนย้ายอุปกรณ์")

    TRANSFER_COLUMNS = ["วันที่โอนย้าย", "Serial Number", "อุปกรณ์", "จากสาขา/สถานที่", "ไปสาขา/สถานที่", "ผู้โอนย้าย", "สถานะการขนส่ง"]
    
    try:
        df = conn.read(worksheet="Transfer Logs", ttl="0")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            for col in TRANSFER_COLUMNS:
                if col not in df.columns: df[col] = ""
            df = df[TRANSFER_COLUMNS]
        else:
            df = pd.DataFrame(columns=TRANSFER_COLUMNS)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูล: {e}")
        df = pd.DataFrame(columns=TRANSFER_COLUMNS)

    BRANCH_LIST = ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม"] # (ย่อส่วน list ให้เหลือเท่านี้เพื่อประหยัดพื้นที่)

    # --- ฟอร์มบันทึก ---
    with st.expander("✈️ บันทึกรายการโอนย้ายอุปกรณ์ใหม่"):
        with st.form("transfer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                t_sn = st.text_input("Serial Number อุปกรณ์:")
                t_device = st.text_input("ชื่อ/ประเภทอุปกรณ์:")
                t_from = st.selectbox("ต้นทาง:", BRANCH_LIST)
            with col2:
                t_to = st.selectbox("ปลายทาง:", BRANCH_LIST)
                t_user = st.text_input("ชื่อผู้โอนย้าย:")
                t_status = st.selectbox("สถานะ:", ["ระหว่างขนส่ง", "ถึงปลายทางแล้ว", "ยกเลิก"])
            
            if st.form_submit_button("💾 บันทึกการโอนย้าย"):
                if t_sn.strip():
                    new_row = pd.DataFrame([{"วันที่โอนย้าย": datetime.now().strftime("%Y-%m-%d %H:%M"), "Serial Number": t_sn, "อุปกรณ์": t_device, "จากสาขา/สถานที่": t_from, "ไปสาขา/สถานที่": t_to, "ผู้โอนย้าย": t_user, "สถานะการขนส่ง": t_status}])
                    conn.update(worksheet="Transfer Logs", data=pd.concat([df, new_row], ignore_index=True).astype(str))
                    st.rerun()

    # --- ตาราง ---
    st.data_editor(df, use_container_width=True, hide_index=True)
