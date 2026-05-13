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

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # --- เนื้อหา PDF (เหมือนเดิม) ---
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Asset Transfer Request Form", 0, 1, "C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Asset Details", 0, 1)
    
    pdf.set_font("Arial", "", 10)
    # ฟังก์ชันช่วยล้างค่าภาษาไทยเพื่อป้องกัน Error
    def clean_text(text):
        return str(text).encode('ascii', 'ignore').decode('ascii')

    pdf.cell(0, 8, f"S/N: {clean_text(data['sn'])}", 0, 1)
    pdf.cell(0, 8, f"Model: {clean_text(data['model'])}", 0, 1)
    pdf.cell(0, 8, f"To: {clean_text(data['to_loc'])}", 0, 1)
    pdf.ln(10)

    # ตารางลายเซ็น (สร้างเป็นช่องว่าง)
    pdf.set_font("Arial", "B", 10)
    col_w = 63
    pdf.cell(col_w, 10, "1. Sender", 1, 0, "C")
    pdf.cell(col_w, 10, "2. Receiver", 1, 0, "C")
    pdf.cell(col_w, 10, "3. Mover", 1, 1, "C")
    
    for _ in range(2): 
        pdf.cell(col_w, 30, "", 1, 0)
        pdf.cell(col_w, 30, "", 1, 0)
        pdf.cell(col_w, 30, "", 1, 1)
        pdf.set_font("Arial", "", 8)
        pdf.cell(col_w, 5, "Signature & Date", 0, 0, "C")
        pdf.cell(col_w, 5, "Signature & Date", 0, 0, "C")
        pdf.cell(col_w, 5, "Signature & Date", 0, 1, "C")
        pdf.ln(5)

    # --- จุดที่แก้ไข: การส่งออกไฟล์เป็น Bytes ---
    # fpdf2.output() ถ้าไม่ระบุชื่อไฟล์ มันจะคืนค่าเป็น bytearray/bytes
    return pdf.output()

# --- ส่วนของปุ่ม ---
if st.button("📥 ออกใบโอนย้าย (PDF)"):
    now_th = datetime.now() + timedelta(hours=7)
    data_to_pdf = {
        "sn": target_sn,
        "model": asset_info['Model Name (ชื่อรุ่น)'],
        "to_loc": to_location,
        "date_ref": now_th.strftime('%Y%m%d')
    }
    
    # สร้าง PDF และแปลงเป็น bytes ให้ชัวร์
    pdf_data = create_pdf(data_to_pdf)
    
    # แปลง bytearray เป็น bytes เพื่อให้ Streamlit download_button ยอมรับ
    pdf_bytes = bytes(pdf_data) 
    
    st.download_button(
        label="Click here to Download PDF",
        data=pdf_bytes,  # ส่ง bytes เข้าไปตรงๆ
        file_name=f"Transfer_{target_sn}.pdf",
        mime="application/pdf"
    )
