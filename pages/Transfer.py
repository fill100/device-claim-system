import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="Asset Transfer Form", layout="wide")

# --- 1. ฟังก์ชันสร้าง PDF ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "FTS-LOGO-01.png")
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")

    # --- Header ตามภาพ image_3c106e.png ---
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=45)
    
    if os.path.exists(font_path):
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_path)
        pdf.set_font('THSarabun', 'B', 14)
    
    pdf.set_y(12) 
    pdf.cell(0, 7, "กิจการร่วมค้า ฟิวเจอร์ สกาย (สำนักงานใหญ่)", 0, 1, "R")
    pdf.set_font('THSarabun', '', 11)
    pdf.cell(0, 6, "เลขที่ 554/72, 554/73, 554/74 อาคารสกายไลน์ เซ็นเตอร์ ชั้น 15", 0, 1, "R")
    pdf.cell(0, 6, "ถนนอโศก-ดินแดง แขวงดินแดง เขตดินแดง กรุงเทพมหานคร 10400", 0, 1, "R")
    
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.6)
    pdf.line(10, 35, 200, 35) 
    
    pdf.ln(12)
    pdf.set_font('THSarabun', 'B', 18)
    pdf.cell(0, 10, "แบบฟอร์มการส่งมอบและโยกย้ายทรัพย์สิน", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 14)
    pdf.cell(0, 8, f"วันที่ดำเนินการ: {data['date']}", 0, 1, "R")
    pdf.cell(0, 8, f"สถานที่ปลายทาง: {data['to_loc']}", 0, 1, "L")
    pdf.ln(5)

    # --- 2. ตารางรายการทรัพย์สิน (Manual Entry) ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    
    w_no, w_asset, w_note = 15, 80, 95
    h_cell = 10

    pdf.cell(w_no, h_cell, "ลำดับ", 1, 0, "C", True)
    pdf.cell(w_asset, h_cell, "เลขทรัพย์สิน / รายการอุปกรณ์", 1, 0, "C", True)
    pdf.cell(w_note, h_cell, "หมายเหตุรายรายการ", 1, 1, "C", True)

    pdf.set_font('THSarabun', '', 14)
    for i, row in enumerate(data['items'], 1):
        asset_val = str(row.get("เลขทรัพย์สิน/ชื่อรายการ", ""))
        note_val = str(row.get("หมายเหตุ", ""))
        pdf.cell(w_no, h_cell, str(i), 1, 0, "C")
        pdf.cell(w_asset, h_cell, f" {asset_val}", 1, 0, "L")
        pdf.cell(w_note, h_cell, f" {note_val}", 1, 1, "L")
    
    # --- 3. Footer ตามภาพ image_3c108a.png ---
    pdf.ln(7)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.multi_cell(0, 6, "ข้าพเจ้ายืนยันว่าได้รับ/ส่งมอบอุปกรณ์ข้างต้นในสภาพสมบูรณ์ หากเกิดความเสียหายจากการใช้งานผิดประเภทข้าพเจ้ายินดีรับผิดชอบตามระเบียบของบริษัท", align="C")

    pdf.ln(5)
    w_sign = 63.3
    pdf.set_font('THSarabun', 'B', 11)
    
    # บรรทัดหัวข้อลายเซ็น
    pdf.cell(w_sign, 7, "1. ผู้ถือครองเดิม (ต้นทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "2. ผู้ถือครองใหม่ (ปลายทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "3. ผู้ดำเนินการโยกย้าย", 0, 1, "C")

    pdf.ln(10)
    # บรรทัดขีดเส้นเซ็น (ชุดที่ 1)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    
    # ชื่อผู้พิมพ์ (ชุดที่ 1)
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, f"( {data['s_old']} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data['s_new']} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data['it_staff']} )", 0, 1, "C")

    pdf.ln(8)
    # บรรทัดขีดเส้นเซ็น (ชุดที่ 2 - หัวหน้า)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    
    # ตำแหน่ง (ชุดที่ 2)
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, "( หัวหน้าต้นทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าปลายทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าฝ่าย IT )", 0, 1, "C")

    return pdf.output()

# --- ส่วน UI ---
st.title("📦 ระบบพิมพ์ใบโอนย้ายทรัพย์สิน (Manual + Full Format)")

if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame([{"เลขทรัพย์สิน/ชื่อรายการ": "", "หมายเหตุ": ""}])

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("**รายการทรัพย์สิน (เพิ่มแถวได้ไม่จำกัด)**")
        edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
    with col2:
        st.write("**ข้อมูลผู้ดำเนินการ**")
        to_location = st.text_input("สถานที่ปลายทาง", placeholder="เช่น คลังสินค้า B")
        s_old = st.text_input("ชื่อผู้ถือครองเดิม (ต้นทาง)", placeholder="พิมพ์ชื่อ-นามสกุล")
        s_new = st.text_input("ชื่อผู้ถือครองใหม่ (ปลายทาง)", placeholder="พิมพ์ชื่อ-นามสกุล")
        it_staff = st.text_input("ชื่อผู้ดำเนินการ (IT)", placeholder="พิมพ์ชื่อ-นามสกุล")

if st.button("🚀 Generate PDF"):
    clean_items = edited_df[edited_df["เลขทรัพย์สิน/ชื่อรายการ"].str.strip() != ""].to_dict('records')
    
    if not clean_items or not to_location:
        st.error("⚠️ กรุณากรอกรายการและสถานที่ปลายทางให้เรียบร้อย")
    else:
        pdf_data = {
            "date": (datetime.now() + timedelta(hours=7)).strftime('%d/%m/%Y'),
            "items": clean_items,
            "to_loc": to_location,
            "s_old": s_old if s_old else "............................",
            "s_new": s_new if s_new else "............................",
            "it_staff": it_staff if it_staff else "............................"
        }
        
        try:
            pdf_out = create_transfer_pdf(pdf_data)
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ PDF",
                data=bytes(pdf_out),
                file_name=f"Transfer_Form_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.success("✅ สร้างไฟล์พร้อมหัวกระดาษและลายเซ็นครบถ้วนแล้ว!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
