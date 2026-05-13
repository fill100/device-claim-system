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
import os

def create_transfer_pdf(data):
    # ใช้ fpdf2
    pdf = FPDF()
    pdf.add_page()
    
    # --- ส่วนการจัดการ Font ---
    # ตรวจสอบว่าไฟล์ Font อยู่ในเครื่องจริงไหม
    font_path = "THSarabunNew.ttf"
    font_bold_path = "THSarabunNew_Bold.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font('THSarabun', '', font_path)
        # ถ้ามีตัวหนาก็ใส่เพิ่ม ถ้าไม่มีให้ใช้ตัวธรรมดาก่อนเพื่อไม่ให้ Error
        if os.path.exists(font_bold_path):
            pdf.add_font('THSarabun', 'B', font_bold_path)
        else:
            pdf.add_font('THSarabun', 'B', font_path) 
            
        pdf.set_font('THSarabun', 'B', 20)
        font_main = 'THSarabun'
    else:
        # ถ้าหาฟอนต์ไม่เจอจริงๆ ให้ใช้ Arial และห้ามใส่ภาษาไทยลงใน Cell
        pdf.set_font('Arial', 'B', 16)
        font_main = 'Arial'
        st.error("⚠️ ไม่พบไฟล์ THSarabunNew.ttf ในระบบ โปรดอัปโหลดไฟล์ฟอนต์ขึ้น GitHub")

    # --- เริ่มสร้างเนื้อหา (ถ้าใช้ Arial จะใช้ภาษาอังกฤษแทนอัตโนมัติ) ---
    def t(thai_text, eng_text):
        return thai_text if font_main == 'THSarabun' else eng_text

    # หัวข้อ
    pdf.cell(0, 10, t("แบบฟอร์มการส่งมอบทรัพย์สินแผนก IT", "IT Asset Handover Form"), 0, 1, "C")
    pdf.ln(5)

    pdf.set_font(font_main, '', 14)
    pdf.cell(0, 10, f"{t('วันที่', 'Date')}: {data['date']}", 0, 1, "R")

    # ข้อมูลพนักงาน
    pdf.cell(0, 10, f"{t('ชื่อ - นามสกุล', 'Name')}: {data['receiver']}     {t('ฝ่าย', 'Dept')}: ...........", 0, 1)
    pdf.cell(0, 10, f"{t('เบอร์โทรศัพท์', 'Tel')}: ........... {t('สถานที่ทำงาน', 'Work Location')}: {data['to_loc']}", 0, 1)
    
    # รายละเอียดอุปกรณ์ (ใช้เส้นบรรทัด)
    pdf.ln(5)
    pdf.set_font(font_main, 'B', 14)
    pdf.cell(0, 10, t("รายละเอียดอุปกรณ์:", "Device Details:"), 0, 1)
    pdf.set_font(font_main, '', 14)
    pdf.cell(0, 10, f"- {t('หมายเลขเครื่อง (S/N)', 'Serial Number')}: {data['sn']}", 0, 1)
    pdf.cell(0, 10, f"- {t('รุ่นอุปกรณ์ (Model)', 'Model')}: {data['model']}", 0, 1)
    pdf.cell(0, 10, f"- {t('หมายเหตุ', 'Remark')}: {data['reason']}", 0, 1)
    
    # ข้อความรับผิดชอบ
    pdf.ln(10)
    pdf.set_font(font_main, 'B', 12)
    notice = t(
        "ข้าพเจ้าขอรับรองว่าจะดูแลรักษาอุปกรณ์ที่รับมอบเป็นอย่างดี หากเสียหายข้าพเจ้าจะขอรับผิดชอบทั้งหมด",
        "I certify that I will take good care of the assigned equipment."
    )
    pdf.multi_cell(0, 7, notice, align="C")

    # --- ตารางลายเซ็น 3 ฝ่าย (ตามรูป image_576ca1) ---
    pdf.ln(15)
    col_w = 60
    pdf.set_font(font_main, 'B', 12)
    pdf.cell(col_w, 10, t("ลงชื่อพนักงาน", "Staff Signature"), 0, 0, "C")
    pdf.cell(col_w, 10, t("ลงชื่อพนักงาน IT", "IT Staff Signature"), 0, 0, "C")
    pdf.cell(col_w, 10, t("ลงชื่อหัวหน้า IT", "Manager Signature"), 0, 1, "C")

    pdf.ln(15) # เว้นที่ว่างให้เซ็นจริง

    pdf.set_font(font_main, '', 12)
    pdf.cell(col_w, 10, f"( {data['receiver']} )", 0, 0, "C")
    pdf.cell(col_w, 10, f"( {data['sender']} )", 0, 0, "C")
    pdf.cell(col_w, 10, f"( {data['manager']} )", 0, 1, "C")

    return pdf.output()
