import streamlit as st
import pandas as pd
from datetime import datetime

# ห่อโค้ดทั้งหมดในฟังก์ชันนี้ เพื่อรองรับการเรียกจาก app.py และรับค่าเชื่อมต่อฐานข้อมูล (conn)
def show_transfer_system(conn):
    st.title("✈️ Transfer Management System")
    st.subheader("ระบบโอนย้ายอุปกรณ์")

    # --- 1. กำหนดโครงสร้างข้อมูล ---
    TRANSFER_COLUMNS = ["วันที่โอนย้าย", "Serial Number", "อุปกรณ์", "จากสาขา/สถานที่", "ไปสาขา/สถานที่", "ผู้โอนย้าย", "สถานะการขนส่ง"]

    # --- 2. ดึงข้อมูลจาก Google Sheets ---
    try:
        # ดึงข้อมูลจาก Worksheet ที่ชื่อว่า "Transfer Logs" (หรือปรับเปลี่ยนชื่อตามตารางจริงของคุณได้เลยครับ)
        df = conn.read(worksheet="Transfer Logs", ttl="0")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # ตรวจสอบคอลัมน์ให้ครบตามโครงสร้าง
            for col in TRANSFER_COLUMNS:
                if col not in df.columns: df[col] = ""
            df = df[TRANSFER_COLUMNS]
        else:
            df = pd.DataFrame(columns=TRANSFER_COLUMNS)
    except Exception:
        df = pd.DataFrame(columns=TRANSFER_COLUMNS)

    # รายชื่อสาขามาตรฐานเพื่อใช้ในฟอร์ม (อ้างอิงตามหน้าหลัก)
    BRANCH_LIST = [
        "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "กรุงเทพมหานคร 5 (สจก.9)", 
        "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)", "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", 
        "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", 
        "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", 
        "จันทบุรี", "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร", 
        "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", 
        "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง", "ระนอง", 
        "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", 
        "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"
    ]

    # --- 3. ฟอร์มบันทึกการโอนย้ายใหม่ ---
    with st.expander("✈️ บันทึกรายการโอนย้ายอุปกรณ์ใหม่", expanded=False):
        with st.form("transfer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                t_sn = st.text_input("Serial Number อุปกรณ์:")
                t_device = st.text_input("ชื่อ/ประเภทอุปกรณ์ (เช่น PC, Monitor):")
                t_from = st.selectbox("ต้นทาง (จากสาขา):", BRANCH_LIST, key="tf_from")
            with col2:
                t_to = st.selectbox("ปลายทาง (ไปสาขา):", BRANCH_LIST, key="tf_to")
                t_user = st.text_input("ชื่อผู้ดำเนินเรื่อง / ผู้โอนย้าย:")
                t_status = st.selectbox("สถานะการขนส่ง:", ["ระหว่างขนส่ง", "ถึงปลายทางแล้ว", "ยกเลิก"])
            
            submit_transfer = st.form_submit_button("💾 บันทึกการโอนย้าย", type="primary")

            if submit_transfer:
                if t_sn.strip() != "" and t_device.strip() != "":
                    now_thailand = datetime.now()
                    time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
                    
                    new_transfer_data = {
                        "วันที่โอนย้าย": time_str,
                        "Serial Number": str(t_sn),
                        "อุปกรณ์": str(t_device),
                        "จากสาขา/สถานที่": str(t_from),
                        "ไปสาขา/สถานที่": str(t_to),
                        "ผู้โอนย้าย": str(t_user),
                        "สถานะการขนส่ง": str(t_status)
                    }
                    
                    try:
                        new_row_df = pd.DataFrame([new_transfer_data])
                        df = pd.concat([df, new_row_df], ignore_index=True)
                        
                        conn.update(worksheet="Transfer Logs", data=df.astype(str))
                        st.success("🎉 บันทึกข้อมูลการโอนย้ายลงระบบสำเร็จ!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ ไม่สามารถบันทึกได้เนื่องจาก: {e}")
                else:
                    st.warning("⚠️ โปรดระบุ Serial Number และ ชื่ออุปกรณ์ ให้ครบถ้วนก่อนบันทึก")

    # --- 4. ตารางแสดงรายการโอนย้ายพร้อมช่องค้นหา ---
    st.divider()
    st.markdown("#### 🔍 ค้นหาและดูประวัติการโอนย้าย ทั้งหมด")
    
    search_q = st.text_input("พิมพ์เพื่อค้นหา (S/N, อุปกรณ์, สาขา...):", key="search_transfer")
    
    view_df = df.copy()
    if search_q:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        view_df = view_df[mask]

    # ตารางแบบ data_editor เพื่อให้เปลี่ยนสถานะการขนส่งได้สะดวก
    edited_transfer_df = st.data_editor(
        view_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "วันที่โอนย้าย": st.column_config.TextColumn(disabled=True),
            "Serial Number": st.column_config.TextColumn(disabled=True),
            "อุปกรณ์": st.column_config.TextColumn(disabled=True),
            "จากสาขา/สถานที่": st.column_config.TextColumn(disabled=True),
            "ไปสาขา/สถานที่": st.column_config.TextColumn(disabled=True),
            "ผู้โอนย้าย": st.column_config.TextColumn(disabled=True),
            "สถานะการขนส่ง": st.column_config.SelectboxColumn("สถานะการขนส่ง", options=["ระหว่างขนส่ง", "ถึงปลายทางแล้ว", "ยกเลิก"], disabled=False)
        },
        key="edit_transfer_status_table"
    )

    # ปุ่มสำหรับบันทึกกรณีมีการแก้ไขสถานะบนตาราง
    if st.button("✅ อัปเดตสถานะการขนส่งที่แก้ไข"):
        try:
            for idx, row in edited_transfer_df.iterrows():
                sn_key = row["Serial Number"]
                new_status = row["สถานะการขนส่ง"]
                df.loc[df["Serial Number"] == sn_key, "สถานะการขนส่ง"] = new_status
            
            conn.update(worksheet="Transfer Logs", data=df.astype(str))
            st.success("🎉 อัปเดตสถานะการขนส่งลงระบบกูเกิ้ลชีตเรียบร้อยแล้ว!")
            st.rerun()
        except Exception as e:
            st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
