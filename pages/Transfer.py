import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="Asset Transfer Form", layout="wide")

with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.page_link("pages/Transfer.py", label="โอนย้ายของ", icon="✈️")

# --- 1. ฟังก์ชันสร้าง PDF ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")

    if os.path.exists(font_path):
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_path)
        pdf.set_font('THSarabun', 'B', 16)
    
    # Header
    pdf.cell(0, 10, "แบบฟอร์มการส่งมอบและโยกย้ายทรัพย์สิน", 0, 1, "C")
    pdf.set_font('THSarabun', '', 14)
    pdf.cell(0, 8, f"วันที่ดำเนินการ: {data['date']}", 0, 1, "R")
    pdf.cell(0, 8, f"สถานที่ปลายทาง: {data['to_loc']}", 0, 1, "L")
    pdf.ln(5)

    # --- ตารางรายการทรัพย์สิน ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    
    # กำหนดความกว้างคอลัมน์
    w_no, w_asset, w_note = 15, 75, 100
    h_cell = 10

    # หัวตาราง
    pdf.cell(w_no, h_cell, "ลำดับ", 1, 0, "C", True)
    pdf.cell(w_asset, h_cell, "เลขทรัพย์สิน / รายการ", 1, 0, "C", True)
    pdf.cell(w_note, h_cell, "หมายเหตุรายรายการ", 1, 1, "C", True)

    # เนื้อหาจาก Editor
    pdf.set_font('THSarabun', '', 14)
    for i, row in enumerate(data['items'], 1):
        # ป้องกันค่าว่าง
        asset_val = str(row.get("เลขทรัพย์สิน/ชื่อรายการ", ""))
        note_val = str(row.get("หมายเหตุ", ""))
        
        pdf.cell(w_no, h_cell, str(i), 1, 0, "C")
        pdf.cell(w_asset, h_cell, f" {asset_val[:40]}", 1, 0, "L")
        pdf.cell(w_note, h_cell, f" {note_val[:55]}", 1, 1, "L")
    
    # --- ส่วนท้าย: ลายเซ็น ---
    pdf.ln(15)
    w_sign = 63.3
    pdf.cell(w_sign, 7, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 7, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 7, "______________________", 0, 1, "C")
    pdf.cell(w_sign, 7, f"( {data['s_old']} )", 0, 0, "C")
    pdf.cell(w_sign, 7, f"( {data['s_new']} )", 0, 0, "C")
    pdf.cell(w_sign, 7, f"( {data['it_staff']} )", 0, 1, "C")
    pdf.cell(w_sign, 7, "ผู้ส่งมอบ", 0, 0, "C")
    pdf.cell(w_sign, 7, "ผู้รับมอบ", 0, 0, "C")
    pdf.cell(w_sign, 7, "เจ้าหน้าที่ IT", 0, 1, "C")

    return pdf.output()

# --- 2. ส่วนหน้าจอ UI ---
st.title("📑 ระบบพิมพ์ใบโอนย้ายทรัพย์สิน (Manual Entry)")
st.info("💡 คุณสามารถพิมพ์เลขทรัพย์สินและหมายเหตุลงในตารางด้านล่างได้เลย (กดปุ่ม + เพื่อเพิ่มแถว)")

# เตรียมโครงสร้างตารางเริ่มต้น
if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame(
        [{"เลขทรัพย์สิน/ชื่อรายการ": "", "หมายเหตุ": ""}],
    )

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        # ตารางแก้ไขข้อมูล (Data Editor)
        st.write("**รายการทรัพย์สินที่ต้องการโอนย้าย**")
        edited_df = st.data_editor(
            st.session_state.df_data,
            num_rows="dynamic", # ให้ผู้ใช้เพิ่ม/ลบแถวได้เอง
            use_container_width=True,
            column_config={
                "เลขทรัพย์สิน/ชื่อรายการ": st.column_config.TextColumn(width="large", help="พิมพ์เลขทรัพย์สินหรือชื่ออุปกรณ์"),
                "หมายเหตุ": st.column_config.TextColumn(width="large", help="ใส่เหตุผลหรือสภาพเครื่อง")
            }
        )
    with col2:
        st.write("**ข้อมูลการโอนย้าย**")
        to_location = st.text_input("สถานที่ปลายทาง")
        s_old = st.text_input("ชื่อผู้ส่งมอบ")
        s_new = st.text_input("ชื่อผู้รับมอบ")
        it_staff = st.text_input("ชื่อเจ้าหน้าที่ IT")

# --- 3. การประมวลผล ---
if st.button("🚀 สร้างไฟล์ PDF"):
    # กรองเอาเฉพาะแถวที่มีข้อมูลเลขทรัพย์สิน
    clean_items = edited_df[edited_df["เลขทรัพย์สิน/ชื่อรายการ"].str.strip() != ""].to_dict('records')
    
    if not clean_items:
        st.warning("⚠️ กรุณากรอกรายการทรัพย์สินอย่างน้อย 1 รายการ")
    elif not to_location:
        st.warning("⚠️ กรุณาระบุสถานที่ปลายทาง")
    else:
        pdf_data = {
            "date": (datetime.now() + timedelta(hours=7)).strftime('%d/%m/%Y'),
            "items": clean_items,
            "to_loc": to_location,
            "s_old": s_old if s_old else "................",
            "s_new": s_new if s_new else "................",
            "it_staff": it_staff if it_staff else "................"
        }
        
        try:
            pdf_out = create_transfer_pdf(pdf_data)
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ PDF",
                data=bytes(pdf_out),
                file_name=f"Transfer_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.success("✅ สร้างไฟล์ PDF เรียบร้อยแล้ว!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
