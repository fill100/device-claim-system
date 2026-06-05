import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# --- 1. ฟังก์ชันสร้าง PDF (แก้ไขแล้ว) ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")
    logo_path = os.path.join(current_dir, "FTS-LOGO-01.png")

    # ตั้งค่าฟอนต์ (ต้องมี uni=True สำหรับภาษาไทย)
    if os.path.exists(font_path):
        pdf.add_font('THSarabun', '', font_path, uni=True)
        pdf.add_font('THSarabun', 'B', font_path, uni=True)
        pdf.set_font('THSarabun', 'B', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Warning: Font not found!", 0, 1, "C")

    # Header
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=45)
    
    pdf.set_y(12) 
    pdf.cell(0, 7, "กิจการร่วมค้า ฟิวเจอร์ สกาย (สำนักงานใหญ่)", 0, 1, "R")
    pdf.set_font('THSarabun', '', 11)
    pdf.cell(0, 6, "เลขที่ 554/72, 554/73, 554/74 อาคารสกายไลน์ เซ็นเตอร์ ชั้น 15", 0, 1, "R")
    pdf.cell(0, 6, "ถนนอโศก-ดินแดง แขวงดินแดง เขตดินแดง กรุงเทพมหานคร 10400", 0, 1, "R")
    
    pdf.line(10, 35, 200, 35) 
    pdf.ln(12)
    pdf.set_font('THSarabun', 'B', 18)
    pdf.cell(0, 10, "แบบฟอร์มการส่งมอบและโยกย้ายทรัพย์สิน", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 14)
    pdf.cell(0, 8, f"วันที่ดำเนินการ: {data['date']}", 0, 1, "R")
    pdf.cell(0, 8, f"สถานที่ปลายทาง: {data['to_loc']}", 0, 1, "L")
    pdf.ln(2)

    # Checkbox
    pdf.set_font('THSarabun', 'B', 14)
    pdf.cell(0, 8, "ประเภทการดำเนินการ:", 0, 1)
    
    types = ["โอนย้ายปกติ", "ส่งซ่อม/เคลม", "ตัดจำหน่าย", "อื่นๆ"]
    x_pos = [15, 55, 95, 135]
    
    for i, t_name in enumerate(types):
        pdf.rect(x_pos[i], pdf.get_y()+2, 4, 4)
        if data['transfer_type'] == t_name:
            pdf.set_xy(x_pos[i]+0.5, pdf.get_y()+2)
            pdf.cell(4, 4, "X", 0, 0, "C")
        pdf.set_xy(x_pos[i]+7, pdf.get_y())
        display_name = t_name if t_name != "อื่นๆ" else "อื่นๆ............................."
        pdf.cell(40, 8, display_name, 0, 0)
    pdf.ln(10)

    # ตาราง
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(15, 10, "ลำดับ", 1, 0, "C", True)
    pdf.cell(80, 10, "เลขทรัพย์สิน / รายการอุปกรณ์", 1, 0, "C", True)
    pdf.cell(95, 10, "หมายเหตุ", 1, 1, "C", True)

    pdf.set_font('THSarabun', '', 14)
    for i, row in enumerate(data['items'], 1):
        pdf.cell(15, 10, str(i), 1, 0, "C")
        pdf.cell(80, 10, f" {row.get('เลขทรัพย์สิน/ชื่อรายการ', '')}", 1, 0, "L")
        pdf.cell(95, 10, f" {row.get('หมายเหตุ', '')}", 1, 1, "L")
    
    # ลายเซ็น
    pdf.ln(10)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.multi_cell(0, 6, "ข้าพเจ้ายืนยันว่าได้รับ/ส่งมอบอุปกรณ์ข้างต้นในสภาพสมบูรณ์ หากเกิดความเสียหายจากการใช้งานผิดประเภทข้าพเจ้ายินดีรับผิดชอบตามระเบียบของบริษัท", align="C")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 2. ส่วน UI ---
st.title("📦 ระบบพิมพ์ใบโอนย้ายทรัพย์สิน")

if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame([{"เลขทรัพย์สิน/ชื่อรายการ": "", "หมายเหตุ": ""}])

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        transfer_type = st.radio("**ประเภทการดำเนินการ**", ["โอนย้ายปกติ", "ส่งซ่อม/เคลม", "ตัดจำหน่าย", "อื่นๆ"], horizontal=True)
        st.write("---")
        edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
    with col2:
        to_location = st.text_input("สถานที่ปลายทาง")
        s_old = st.text_input("ชื่อผู้ถือครองเดิม")
        s_new = st.text_input("ชื่อผู้ถือครองใหม่")
        it_staff = st.text_input("ชื่อผู้ดำเนินการ (IT)")

if st.button("🚀 Generate PDF"):
    clean_items = edited_df[edited_df["เลขทรัพย์สิน/ชื่อรายการ"].str.strip() != ""].to_dict('records')
    if not clean_items or not to_location:
        st.error("⚠️ กรุณากรอกรายการและสถานที่ปลายทาง")
    else:
        pdf_data = {
            "date": (datetime.now() + timedelta(hours=7)).strftime('%d/%m/%Y'),
            "items": clean_items,
            "to_loc": to_location,
            "transfer_type": transfer_type,
            "s_old": s_old if s_old else "............................",
            "s_new": s_new if s_new else "............................",
            "it_staff": it_staff if it_staff else "............................"
        }
        try:
            pdf_out = create_transfer_pdf(pdf_data)
            st.download_button(label="📥 ดาวน์โหลดไฟล์ PDF", data=pdf_out, file_name="Transfer_Form.pdf", mime="application/pdf")
            st.success("✅ พร้อมดาวน์โหลดแล้วครับ!")
        except Exception as e:
            st.error(f"Error: {e}")
