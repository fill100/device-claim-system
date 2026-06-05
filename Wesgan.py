import streamlit as st
import pandas as pd
from datetime import datetime

def run_transfer_page(conn):
    # ปรับแต่ง Header ให้ดูสะอาดขึ้น
    st.title("✈️ Transfer Management System")
    st.markdown("---")

    TRANSFER_COLUMNS = ["วันที่โอนย้าย", "Serial Number", "อุปกรณ์", "จากสาขา/สถานที่", "ไปสาขา/สถานที่", "ผู้โอนย้าย", "สถานะการขนส่ง"]
    
    # ดึงข้อมูล
    try:
        df = conn.read(worksheet="Transfer Logs", ttl="0")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # เติมคอลัมน์ที่ขาดหายไปให้ครบ
            for col in TRANSFER_COLUMNS:
                if col not in df.columns: df[col] = ""
            df = df[TRANSFER_COLUMNS].astype(str)
        else:
            df = pd.DataFrame(columns=TRANSFER_COLUMNS)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูล: {e}")
        df = pd.DataFrame(columns=TRANSFER_COLUMNS)

    BRANCH_LIST = ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม"]

    # --- ส่วนบันทึกข้อมูล ---
    with st.expander("✈️ บันทึกรายการโอนย้ายอุปกรณ์ใหม่", expanded=False):
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
            
            if st.form_submit_button("💾 บันทึกการโอนย้าย", type="primary"):
                if t_sn.strip() != "":
                    new_data = {
                        "วันที่โอนย้าย": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Serial Number": t_sn,
                        "อุปกรณ์": t_device,
                        "จากสาขา/สถานที่": t_from,
                        "ไปสาขา/สถานที่": t_to,
                        "ผู้โอนย้าย": t_user,
                        "สถานะการขนส่ง": t_status
                    }
                    new_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    conn.update(worksheet="Transfer Logs", data=new_df)
                    st.success("บันทึกสำเร็จ!")
                    st.rerun()
                else:
                    st.warning("กรุณาระบุ Serial Number")

    # --- ส่วนแสดงตาราง ---
    st.subheader("📋 ประวัติการโอนย้าย")
    # เปลี่ยนจาก use_container_width=True เป็น width='stretch' เพื่อแก้ปัญหาจอดำ
    st.data_editor(
        df, 
        width='stretch', 
        hide_index=True,
        column_config={
            "สถานะการขนส่ง": st.column_config.SelectboxColumn(
                options=["ระหว่างขนส่ง", "ถึงปลายทางแล้ว", "ยกเลิก"]
            )
        }
    )
