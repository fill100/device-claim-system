import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os
from streamlit_gsheets import GSheetsConnection

# --- ตั้งค่าหน้ากระดาษและซ่อนเมนู ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Transfer Form", layout="wide")

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
    logo_path = os.path.join(current_dir, "FTS-LOGO-01.png")
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")

    # Header & Logo
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

    # --- 2. ส่วน Checkbox ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.cell(0, 8, "ประเภทการดำเนินการ:", 0, 1)
    pdf.set_line_width(0.2) # ปรับเส้น Checkbox ให้บางลง
    pdf.set_font('THSarabun', '', 14)
    pdf.rect(15, pdf.get_y()+2, 4, 4); pdf.set_x(22); pdf.cell(40, 8, "โอนย้ายปกติ", 0, 0)
    pdf.rect(55, pdf.get_y()+2, 4, 4); pdf.set_x(62); pdf.cell(40, 8, "ส่งซ่อม/เคลม", 0, 0)
    pdf.rect(95, pdf.get_y()+2, 4, 4); pdf.set_x(102); pdf.cell(40, 8, "ตัดจำหน่าย", 0, 0)
    pdf.rect(135, pdf.get_y()+2, 4, 4); pdf.set_x(142); pdf.cell(40, 8, "อื่นๆ..................", 0, 1)
    pdf.ln(5)

    # --- 3. ตารางรายการอุปกรณ์ ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    
    w_no, w_sn, w_name, w_note = 15, 55, 45, 65
    h_cell = 20

    # หัวตาราง
    pdf.cell(w_no, h_cell, "ลำดับ", 1, 0, "C", True)
    pdf.cell(w_sn, h_cell, "Serial Number", 1, 0, "C", True)
    pdf.cell(w_name, h_cell, "รายการ/รุ่นอุปกรณ์", 1, 0, "C", True)
    pdf.cell(w_note, h_cell, "หมายเหตุ", 1, 1, "C", True)

    # เนื้อหาตาราง
    pdf.set_font('THSarabun', '', 14)
    for i, item in enumerate(data['items'], 1):
        pdf.cell(w_no, h_cell, str(i), 1, 0, "C")
        pdf.cell(w_sn, h_cell, str(item.get('sn', '-')), 1, 0, "C")
        
        model_text = str(item.get('model', '-'))[:35]
        pdf.cell(w_name, h_cell, f" {model_text}", 1, 0, "L")
        
        # ใส่หมายเหตุเฉพาะบรรทัดแรก
        note_text = data.get('reason', '') if i == 1 else ""
        pdf.cell(w_note, h_cell, f" {note_text[:30]}", 1, 1, "L")
    
    pdf.ln(5)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.multi_cell(0, 6, "ข้าพเจ้ายืนยันว่าได้รับ/ส่งมอบอุปกรณ์ข้างต้นในสภาพสมบูรณ์ หากเกิดความเสียหายจากการใช้งานผิดประเภทข้าพเจ้ายินดีรับผิดชอบตามระเบียบของบริษัท", align="C")

    # --- 4. ส่วนลายเซ็น 3 กลุ่ม ---
    pdf.ln(5)
    w_sign = 63.3
    pdf.set_font('THSarabun', 'B', 11)
    
    pdf.cell(w_sign, 7, "1. ผู้ถือครองเดิม (ต้นทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "2. ผู้ถือครองใหม่ (ปลายทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "3. ผู้ดำเนินการโยกย้าย", 0, 1, "C")

    pdf.ln(10)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, f"( {data.get('s_old', '............................')} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data.get('s_new', '............................')} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data.get('it_staff', '............................')} )", 0, 1, "C")

    pdf.ln(8)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, "( หัวหน้าต้นทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าปลายทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าฝ่าย IT )", 0, 1, "C")

    return pdf.output()

# --- 2. การเชื่อมต่อข้อมูลและ UI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_asset = conn.read(worksheet="Asset Management", ttl="0")

st.title("📦 ระบบออกใบโอนย้ายทรัพย์สิน")

if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        selected_sns = st.multiselect("เลือก Serial Number", df_asset["Serial Number (เลขซีเรียล)"].unique())
        to_location = st.text_input("สถานที่ปลายทาง / หน่วยงานที่รับโอน")
    with c2:
        transfer_reason = st.text_area("หมายเหตุ / เหตุผลการโอนย้าย")

    st.divider()
    f1, f2, f3 = st.columns(3)
    with f1:
        s_old = st.text_input("ชื่อผู้ถือครองเดิม")
    with f2:
        s_new = st.text_input("ชื่อผู้ถือครองใหม่")
    with f3:
        it_staff = st.text_input("ชื่อผู้ดำเนินการ (IT)")

# --- 3. ส่วนการประมวลผล ---
if st.button("🚀 เตรียมไฟล์ PDF (Generate)"):
    if not s_new or not to_location or not selected_sns:
        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบและเลือกอุปกรณ์อย่างน้อย 1 รายการ")
    else:
        now_th = datetime.now() + timedelta(hours=7)
        
        selected_items = []
        for sn in selected_sns:
            row = df_asset[df_asset["Serial Number (เลขซีเรียล)"] == sn].iloc[0]
            selected_items.append({
                "sn": sn,
                "model": row['Model Name (ชื่อรุ่น)']
            })

        pdf_data = {
            "date": now_th.strftime('%d/%m/%Y'),
            "items": selected_items,
            "to_loc": to_location,
            "reason": transfer_reason,
            "s_old": s_old,
            "s_new": s_new,
            "it_staff": it_staff
        }
        
        try:
            pdf_out = create_transfer_pdf(pdf_data)
            st.session_state.pdf_ready = bytes(pdf_out)
            st.success("✅ สร้างไฟล์สำเร็จ!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

if st.session_state.pdf_ready is not None:
    st.download_button(
        label="📥 ดาวน์โหลดไฟล์ PDF",
        data=st.session_state.pdf_ready,
        file_name=f"Transfer_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
