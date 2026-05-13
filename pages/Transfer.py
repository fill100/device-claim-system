import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Transfer Request", layout="wide")

# --- ฟังก์ชันสร้าง PDF ---
class TransferForm(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Asset Transfer Request Form', 0, 1, 'C')
        self.ln(5)

def generate_pdf(data):
    pdf = TransferForm()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # ส่วนข้อมูลทั่วไป
    pdf.cell(0, 10, f"Date: {data['date']}", 0, 1)
    pdf.cell(0, 10, f"Asset S/N: {data['sn']}", 0, 1)
    pdf.cell(0, 10, f"Model: {data['model']}", 0, 1)
    pdf.cell(0, 10, f"To Location: {data['to_loc']}", 0, 1)
    pdf.ln(10)
    
    # ส่วนลายเซ็น (สร้างเป็นตาราง 3 คอลัมน์)
    col_width = 60
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(col_width, 10, "1. Original Owner", 1, 0, 'C')
    pdf.cell(col_width, 10, "2. New Owner", 1, 0, 'C')
    pdf.cell(col_width, 10, "3. Mover", 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    # แถวผู้ปฏิบัติงาน
    pdf.cell(col_width, 20, f"Staff: {data['s1']}\n", 1, 0, 'L')
    pdf.cell(col_width, 20, f"Staff: {data['s2']}\n", 1, 0, 'L')
    pdf.cell(col_width, 20, f"Staff: {data['s3']}\n", 1, 1, 'L')
    
    # แถวหัวหน้า
    pdf.cell(col_width, 20, f"Manager: {data['m1']}\n", 1, 0, 'L')
    pdf.cell(col_width, 20, f"Manager: {data['m2']}\n", 1, 0, 'L')
    pdf.cell(col_width, 20, f"Manager: {data['m3']}\n", 1, 1, 'L')
    
    return pdf.output(dest='S').encode('latin-1')

# --- หน้า UI ---
st.title("📦 ใบโอนย้ายทรัพย์สิน (Audit Approved)")

# ดึงข้อมูลทรัพย์สินมาให้เลือก
conn = st.connection("gsheets", type=GSheetsConnection)
df_asset = conn.read(worksheet="Asset Management", ttl="0")

with st.form("transfer_form"):
    st.subheader("1. ข้อมูลทรัพย์สิน")
    target_sn = st.selectbox("เลือก Serial Number", df_asset["Serial Number (เลขซีเรียล)"].tolist())
    reason = st.text_area("เหตุผลการโอนย้าย")
    to_loc = st.text_input("โอนย้ายไปที่หน่วยงาน/สถานที่ใด")
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("เจ้าของเดิม (Sender)")
        s1 = st.text_input("ชื่อเจ้าของเดิม")
        m1 = st.text_input("ชื่อหัวหน้า (เจ้าของเดิม)")
    with c2:
        st.success("เจ้าของใหม่ (Receiver)")
        s2 = st.text_input("ชื่อเจ้าของใหม่")
        m2 = st.text_input("ชื่อหัวหน้า (เจ้าของใหม่)")
    with c3:
        st.warning("ผู้ดำเนินการ (Mover)")
        s3 = st.text_input("ชื่อผู้มาขนย้าย")
        m3 = st.text_input("ชื่อหัวหน้า (ผู้ขนย้าย)")

    if st.form_submit_button("สร้างเอกสารโอนย้าย"):
        # รวบรวมข้อมูล
        asset_info = df_asset[df_asset["Serial Number (เลขซีเรียล)"] == target_sn].iloc[0]
        data = {
            "date": (datetime.now() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M"),
            "sn": target_sn,
            "model": asset_info["Model Name (ชื่อรุ่น)"],
            "to_loc": to_loc,
            "s1": s1, "m1": m1,
            "s2": s2, "m2": m2,
            "s3": s3, "m3": m3
        }
        
        pdf_bytes = generate_pdf(data)
        st.download_button(
            label="📥 ดาวน์โหลดใบโอนย้าย (PDF)",
            data=pdf_bytes,
            file_name=f"Transfer_{target_sn}.pdf",
            mime="application/pdf"
        )
