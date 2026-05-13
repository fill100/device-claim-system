import streamlit as st
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* ซ่อนเมนูเดิมที่ชื่อ app/Wesgan */
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Transfer Form", layout="wide")

with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.page_link("pages/Transfer.py", label="โอนย้ายของ", icon="✈️")

# --- 1. การเชื่อมต่อข้อมูล ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_asset = conn.read(worksheet="Asset Management", ttl="0")
except:
    st.error("ไม่สามารถดึงข้อมูลจาก Asset Management ได้")
    st.stop()

# --- 2. ส่วนของ FORM รับข้อมูล ---
st.title("📦 ระบบออกเอกสารใบโอนย้ายทรัพย์สิน")
st.info("กรอกข้อมูลให้ครบถ้วนเพื่อสร้างใบโอนย้ายสำหรับ Audit")

with st.container(border=True):
    col_a, col_b = st.columns(2)
    with col_a:
        # ดึง S/N มาให้เลือกเพื่อลดความผิดพลาด
        target_sn = st.selectbox("เลือกรหัสทรัพย์สิน (S/N)", df_asset["Serial Number (เลขซีเรียล)"].unique())
        asset_info = df_asset[df_asset["Serial Number (เลขซีเรียล)"] == target_sn].iloc[0]
        st.write(f"**รุ่นที่เลือก:** {asset_info['Model Name (ชื่อรุ่น)']}")
    
    with col_b:
        to_location = st.text_input("สถานที่ปลายทาง / หน่วยงานที่รับโอน")
        transfer_reason = st.text_input("วัตถุประสงค์การโอนย้าย")

    st.divider()
    
    # ส่วนลายเซ็น 3 ฝ่าย
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### ⬅️ ต้นทาง (Sender)")
        s1 = st.text_input("ชื่อเจ้าของเดิม", placeholder="ผู้ส่งมอบ")
        m1 = st.text_input("ชื่อหัวหน้าต้นทาง", placeholder="ผู้อนุมัติส่งมอบ")
    with c2:
        st.markdown("### ➡️ ปลายทาง (Receiver)")
        s2 = st.text_input("ชื่อเจ้าของใหม่", placeholder="ผู้รับมอบ")
        m2 = st.text_input("ชื่อหัวหน้าปลายทาง", placeholder="ผู้อนุมัติรับมอบ")
    with c3:
        st.markdown("### 🚚 ผู้ดำเนินการ (Mover)")
        s3 = st.text_input("ชื่อผู้ขนย้าย", placeholder="ผู้เคลื่อนย้าย")
        m3 = st.text_input("ชื่อหัวหน้าผู้ขนย้าย", placeholder="ผู้อนุมัติการเคลื่อนย้าย")

from fpdf import FPDF
import io

# --- ฟังก์ชันสร้าง PDF รองรับภาษาไทย ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. ลงทะเบียน Font ภาษาไทย (ต้องมีไฟล์ .ttf ในโปรเจกต์)
    # สมมติว่าไฟล์ชื่อ THSarabunNew.ttf อยู่ในโฟลเดอร์เดียวกับไฟล์โค้ด
    try:
        pdf.add_font('THSarabun', '', 'THSarabunNew.ttf')
        pdf.add_font('THSarabun', 'B', 'THSarabunNew_Bold.ttf') # ถ้ามีตัวหนา
        font_name = 'THSarabun'
    except:
        # ถ้าหาไฟล์ฟอนต์ไม่เจอ ให้กลับไปใช้ Arial (ภาษาไทยจะกลายเป็น ?)
        font_name = 'Arial'

    # --- เริ่มวาดฟอร์มตามแบบ image_576ca1 ---
    pdf.set_font(font_name, 'B', 20)
    pdf.cell(0, 10, "แบบฟอร์มการส่งมอบทรัพย์สินแผนก IT", 0, 1, "C")
    pdf.ln(5)

    pdf.set_font(font_name, '', 14)
    pdf.cell(0, 10, f"วันที่: {data['date']}", 0, 1, "R")

    # ข้อมูลพนักงาน
    pdf.cell(0, 10, f"ชื่อ - นามสกุล: {data['receiver']}     ฝ่าย: ........................... แผนก: ...........................", 0, 1)
    pdf.cell(0, 10, f"เบอร์โทรศัพท์: ........................... สถานที่ทำงาน: {data['to_loc']}", 0, 1)
    pdf.ln(5)

    # รายละเอียดอุปกรณ์
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, "รายละเอียดอุปกรณ์:", 0, 1)
    pdf.set_font(font_name, '', 14)
    pdf.cell(0, 10, f"- หมายเลขเครื่อง (S/N): {data['sn']}", 0, 1)
    pdf.cell(0, 10, f"- รุ่นอุปกรณ์ (Model): {data['model']}", 0, 1)
    pdf.cell(0, 10, f"- หมายเหตุ: {data['reason']}", 0, 1)
    pdf.ln(10)

    # ข้อความรับผิดชอบ (ตัวแดงในรูป แต่ PDF จะเป็นตัวหนา)
    pdf.set_font(font_name, 'B', 12)
    notice = "ข้าพเจ้าขอรับรองว่าจะดูแลรักษาอุปกรณ์ที่รับมอบเป็นอย่างดี หากมีความเสียหายหรือสูญหาย ข้าพเจ้าจะขอรับผิดชอบทั้งหมดทุกกรณี"
    pdf.multi_cell(0, 7, notice, align="C")
    pdf.ln(10)

    # --- ตารางลายเซ็น 3 ฝ่าย ---
    col_w = 60
    pdf.set_font(font_name, 'B', 12)
    pdf.cell(col_w, 10, "ลงชื่อพนักงาน", 0, 0, "C")
    pdf.cell(col_w, 10, "ลงชื่อพนักงานฝ่าย IT", 0, 0, "C")
    pdf.cell(col_w, 10, "ลงชื่อหัวหน้าฝ่าย IT", 0, 1, "C")

    # เว้นที่ว่างเซ็นชื่อ
    pdf.ln(15)

    pdf.set_font(font_name, '', 12)
    pdf.cell(col_w, 10, f"( {data['receiver']} )", 0, 0, "C")
    pdf.cell(col_w, 10, f"( {data['sender']} )", 0, 0, "C")
    pdf.cell(col_w, 10, f"( {data['manager']} )", 0, 1, "C")

    pdf.cell(col_w, 10, "ผู้รับมอบ", 0, 0, "C")
    pdf.cell(col_w, 10, "ฝ่ายสารสนเทศ", 0, 0, "C")
    pdf.cell(col_w, 10, "หัวหน้าฝ่ายสารสนเทศ", 0, 1, "C")

    # คืนค่าเป็น Bytes
    return pdf.output()

# --- ส่วนใน Streamlit ---
if st.button(" PDF (สร้างไฟล์ PDF)"):
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
    
    output_pdf = create_transfer_pdf(pdf_data)
    
    st.download_button(
        label="📥 ดาวน์โหลดใบโอนย้าย (PDF)",
        data=bytes(output_pdf),
        file_name=f"Transfer_{target_sn}.pdf",
        mime="application/pdf"
    )
