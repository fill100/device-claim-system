import streamlit as st
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* ซ่อนเมนูเดิมที่ชื่อ app/Wesgan */
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Transfer Form", layout="wide")

with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.page_link("pages/Transfer.py", label="โอนย้ายของ", icon="✈️")

# --- 1. ฟังก์ชันสร้าง PDF (แบบฝังฟอนต์ไทย) ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "FTS-LOGO-01.png")
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")

    # 1. วางโลโก้ (ด้านซ้าย)
    if os.path.exists(logo_path):
        # ปรับ y=10 ให้โลโก้อยู่ในระดับที่สวยงาม
        pdf.image(logo_path, x=10, y=10, w=45)
    
    # 2. ใส่ข้อมูลบริษัท (ชิดขวา)
    if os.path.exists(font_path):
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_path)
        pdf.set_font('THSarabun', 'B', 14)
    else:
        pdf.set_font('Arial', 'B', 12)

    # ปรับตำแหน่ง Y ของตัวหนังสือให้เริ่มต้นที่ 12 (เพื่อให้กึ่งกลางขนานกับโลโก้)
    pdf.set_y(12) 
    
    # ใช้ cell(0, ...) และ align='R' เพื่อให้ข้อความไปชิดขอบขวาสุดของหน้ากระดาษ
    pdf.cell(0, 7, "กิจการร่วมค้า ฟิวเจอร์ สกาย (สำนักงานใหญ่)", 0, 1, "R")
    
    pdf.set_font('THSarabun' if os.path.exists(font_path) else 'Arial', '', 11)
    pdf.cell(0, 6, "เลขที่ 554/72, 554/73, 554/74 อาคารสกายไลน์ เซ็นเตอร์ ชั้น 15", 0, 1, "R")
    pdf.cell(0, 6, "ถนนอโศก-ดินแดง แขวงดินแดง เขตดินแดง กรุงเทพมหานคร 10400", 0, 1, "R")
    
    # 3. วาดเส้นใต้
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.8)
    # ลากเส้นใต้โลโก้และที่อยู่ (ขยับลงมาที่ y=35)
    pdf.line(10, 35, 200, 35) 
    
    pdf.ln(12) # เว้นระยะก่อนเริ่มเนื้อหา
    
    # --- ส่วนหัวข้อแบบฟอร์ม ---
    pdf.set_font('THSarabun' if os.path.exists(font_path) else 'Arial', 'B', 20)
    pdf.cell(0, 15, "แบบฟอร์มการส่งมอบทรัพย์สินแผนก IT", 0, 1, "C")
    
    # --- จบส่วน Header ---
    
    # --- ระบบค้นหา Font แบบยืดหยุ่น ---
    # ลองหาไฟล์จากหลายๆ ที่ที่อาจเป็นไปได้
    possible_paths = [
        "pages/THSarabunNew.ttf",
        "THSarabunNew.ttf",
        os.path.join(os.path.dirname(__file__), "THSarabunNew.ttf")
    ]
    
    font_path = None
    for path in possible_paths:
        if os.path.exists(path):
            font_path = path
            break

    if font_path:
        # ลงทะเบียนทั้งแบบธรรมดาและแบบหนาโดยใช้ไฟล์เดียวกันเพื่อกัน Error set_font('...','B',...)
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_path) 
        font_main = 'THSarabun'
        pdf.set_font(font_main, 'B', 22)
    else:
        # กรณีหาไม่เจอจริงๆ ให้ใช้ Arial และห้ามใส่ภาษาไทย (เพื่อไม่ให้แอปพัง)
        font_main = 'Arial'
        pdf.set_font(font_main, 'B', 16)
        st.error(f"❌ ระบบยังหาไฟล์ฟอนต์ไม่พบ ลองตรวจสอบชื่อไฟล์ใน GitHub อีกครั้ง (ต้องตรงเป๊ะทุกตัวอักษร)")
        # แสดงชื่อไฟล์ที่มีอยู่ในโฟลเดอร์ pages เพื่อช่วย Debug
        try:
            files_in_pages = os.listdir("pages")
            st.write(f"ไฟล์ที่ตรวจพบในโฟลเดอร์ pages: {files_in_pages}")
        except:
            pass

    # --- ส่วนการสร้างเนื้อหา (เหมือนเดิม) ---
    # ใช้ฟังก์ชันช่วยตรวจสอบ ถ้าฟอนต์ไม่ใช่ไทย ให้โชว์อังกฤษแทน
    def txt(thai, eng):
        return thai if font_main == 'THSarabun' else eng
    
    # หัวข้อเอกสาร (ตามสไตล์รูป 576ca1)
    pdf.set_font(font_main, 'B', 22)
    pdf.cell(0, 15, "แบบฟอร์มการส่งมอบทรัพย์สินแผนก IT", 0, 1, "C")
    
    pdf.set_font(font_main, '', 14)
    pdf.cell(0, 10, f"วันที่: {data['date']}", 0, 1, "R")
    pdf.ln(5)

    # รายละเอียดผู้รับ
    pdf.cell(0, 10, f"ชื่อ - นามสกุล: {data['receiver']}      สถานที่ทำงาน: {data['to_loc']}", 0, 1)
    pdf.ln(5)

    # รายละเอียดอุปกรณ์
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(0, 10, "รายละเอียดอุปกรณ์ / Asset Details", 0, 1)
    pdf.set_font(font_main, '', 14)
    pdf.cell(0, 8, f"- หมายเลขเครื่อง (S/N): {data['sn']}", 0, 1)
    pdf.cell(0, 8, f"- รุ่นอุปกรณ์ (Model): {data['model']}", 0, 1)
    pdf.cell(0, 8, f"- หมายเหตุ (Remark): {data['reason']}", 0, 1)
    pdf.ln(10)

    # ข้อความรับผิดชอบ
    pdf.set_font(font_main, 'B', 12)
    notice = "ข้าพเจ้าขอรับรองว่าจะดูแลรักษาอุปกรณ์ที่รับมอบเป็นอย่างดี หากมีความเสียหายหรือสูญหาย ข้าพเจ้าจะขอรับผิดชอบทั้งหมดทุกกรณี"
    pdf.multi_cell(0, 7, notice, align="C")
    pdf.ln(15)

    # ตารางลายเซ็น 3 ฝ่าย (พนักงาน / IT / หัวหน้า IT)
    col_w = 63
    pdf.set_font(font_main, 'B', 13)
    pdf.cell(col_w, 10, "ลงชื่อพนักงาน (ผู้รับมอบ)", 0, 0, "C")
    pdf.cell(col_w, 10, "ลงชื่อพนักงาน IT", 0, 0, "C")
    pdf.cell(col_w, 10, "ลงชื่อหัวหน้าฝ่าย IT", 0, 1, "C")

    pdf.ln(15) # พื้นที่ว่างสำหรับเซ็นชื่อ

    pdf.set_font(font_main, '', 13)
    pdf.cell(col_w, 8, f"( {data['receiver']} )", 0, 0, "C")
    pdf.cell(col_w, 8, f"( {data['sender']} )", 0, 0, "C")
    pdf.cell(col_w, 8, f"( {data['manager']} )", 0, 1, "C")
    
    pdf.set_font(font_main, '', 10)
    pdf.cell(col_w, 8, "วันที่ _____/_____/_____", 0, 0, "C")
    pdf.cell(col_w, 8, "วันที่ _____/_____/_____", 0, 0, "C")
    pdf.cell(col_w, 8, "วันที่ _____/_____/_____", 0, 1, "C")

    return pdf.output()

# --- 2. การเชื่อมต่อข้อมูลและ UI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_asset = conn.read(worksheet="Asset Management", ttl="0")

st.title("📦 ระบบออกใบโอนย้ายทรัพย์สิน")

# ใช้ Session State เก็บไฟล์ PDF เพื่อไม่ให้ปุ่มดาวน์โหลดหายไป
if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None
if 'last_sn' not in st.session_state:
    st.session_state.last_sn = ""

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        target_sn = st.selectbox("เลือก Serial Number", df_asset["Serial Number (เลขซีเรียล)"].unique())
        asset_info = df_asset[df_asset["Serial Number (เลขซีเรียล)"] == target_sn].iloc[0]
        to_location = st.text_input("สถานที่ปลายทาง / หน่วยงานที่รับโอน")
    with c2:
        transfer_reason = st.text_area("หมายเหตุ / เหตุผลการโอนย้าย")

    st.divider()
    
    f1, f2, f3 = st.columns(3)
    with f1:
        s1 = st.text_input("ชื่อพนักงาน IT (ผู้ส่ง)")
    with f2:
        s2 = st.text_input("ชื่อพนักงาน (ผู้รับมอบ)")
    with f3:
        m3 = st.text_input("ชื่อหัวหน้าฝ่าย IT")

# --- 3. ส่วนการประมวลผล ---
if st.button("🚀 เตรียมไฟล์ PDF (Generate)"):
    if not s2 or not to_location:
        st.warning("⚠️ กรุณากรอกชื่อผู้รับและสถานที่ปลายทาง")
    else:
        now_th = datetime.now() + timedelta(hours=7)
        pdf_data = {
            "date": now_th.strftime('%d/%m/%Y'),
            "receiver": s2,
            "sender": s1,
            "manager": m3,
            "to_loc": to_location,
            "sn": target_sn,
            "model": asset_info['Model Name (ชื่อรุ่น)'],
            "reason": transfer_reason,
            "date_ref": now_th.strftime('%Y%m%d')
        }
        
        # สร้าง PDF และบันทึกเข้า session
        pdf_out = create_transfer_pdf(pdf_data)
        st.session_state.pdf_ready = bytes(pdf_out)
        st.session_state.last_sn = target_sn
        st.success("✅ สร้างไฟล์สำเร็จ! กดดาวน์โหลดที่ปุ่มด้านล่าง")

# --- 4. ปุ่มดาวน์โหลด (อยู่นอก if button เพื่อไม่ให้หายไป) ---
if st.session_state.pdf_ready is not None:
    st.download_button(
        label=f"📥 ดาวน์โหลดไฟล์ Transfer_{st.session_state.last_sn}.pdf",
        data=st.session_state.pdf_ready,
        file_name=f"Transfer_{st.session_state.last_sn}.pdf",
        mime="application/pdf"
    )
