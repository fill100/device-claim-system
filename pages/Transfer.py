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

# --- ฟังก์ชันสร้าง PDF ---
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # หัวข้อเอกสาร
    pdf.cell(0, 10, "Asset Transfer Request Form", 0, 1, "C")
    pdf.ln(5)
    
    # ข้อมูลทรัพย์สิน
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Asset Information", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(100, 8, f"Serial Number (S/N): {data['sn']}", 0, 0)
    pdf.cell(0, 8, f"Model: {data['model']}", 0, 1)
    pdf.cell(100, 8, f"Current Location: {data['loc']}", 0, 0)
    pdf.cell(0, 8, f"To Location: {data['to_loc']}", 0, 1)
    pdf.multi_cell(0, 8, f"Reason: {data['reason']}")
    pdf.ln(10)
    
    # ตารางลายเซ็น 3 คอลัมน์ (Sender, Receiver, Mover)
    pdf.set_font("Arial", "B", 10)
    col_w = 63
    pdf.cell(col_w, 10, "1. Sender (Original Owner)", 1, 0, "C")
    pdf.cell(col_w, 10, "2. Receiver (New Owner)", 1, 0, "C")
    pdf.cell(col_w, 10, "3. Mover (Operation)", 1, 1, "C")
    
    # บรรทัดผู้ปฏิบัติงาน (Staff)
    pdf.set_font("Arial", "", 9)
    pdf.cell(col_w, 25, f"Staff: {data['s1']}", 1, 0, "L")
    pdf.cell(col_w, 25, f"Staff: {data['s2']}", 1, 0, "L")
    pdf.cell(col_w, 25, f"Staff: {data['s3']}", 1, 1, "L")
    
    # บรรทัดหัวหน้า (Manager)
    pdf.cell(col_w, 25, f"Manager: {data['m1']}", 1, 0, "L")
    pdf.cell(col_w, 25, f"Manager: {data['m2']}", 1, 0, "L")
    pdf.cell(col_w, 25, f"Manager: {data['m3']}", 1, 1, "L")
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"Audit Ref: {data['sn']}-{data['date_ref']}", 0, 0, "R")
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- ส่วนของปุ่มในหน้า Streamlit ---
if st.button("📄 สร้างไฟล์ PDF สำหรับพิมพ์"):
    if not to_location or not s1 or not s2:
        st.warning("กรุณากรอกข้อมูลสำคัญให้ครบถ้วน")
    else:
        now_th = datetime.now() + timedelta(hours=7)
        data_to_pdf = {
            "sn": target_sn,
            "model": asset_info['Model Name (ชื่อรุ่น)'],
            "loc": asset_info['Location (สถานที่)'],
            "to_loc": to_location,
            "reason": transfer_reason,
            "s1": s1, "m1": m1,
            "s2": s2, "m2": m2,
            "s3": s3, "m3": m3,
            "date_ref": now_th.strftime('%Y%m%d')
        }
        
        pdf_output = create_pdf(data_to_pdf)
        
        st.success("สร้างไฟล์สำเร็จ! กดปุ่มดาวน์โหลดด้านล่างได้เลย")
        st.download_button(
            label="📥 Download Transfer Form (PDF)",
            data=pdf_output,
            file_name=f"Transfer_{target_sn}.pdf",
            mime="application/pdf",
        )
