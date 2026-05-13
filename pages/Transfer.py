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

    # --- 1. Header (เหมือนเดิม) ---
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
    pdf.line(10, 35, 200, 35) 
    
    pdf.ln(10)
    pdf.set_font('THSarabun', 'B', 18)
    pdf.cell(0, 10, "แบบฟอร์มการโยกย้ายทรัพย์สิน IT", 0, 1, "C")
    pdf.set_font('THSarabun', '', 14)
    pdf.cell(0, 8, f"วันที่ดำเนินการ: {data['date']}", 0, 1, "R")

    # --- 2. ส่วน Checkbox การดำเนินการ ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.cell(0, 8, "ประเภทการดำเนินการ:", 0, 1)
    pdf.set_font('THSarabun', '', 14)
    # วาดช่องสี่เหลี่ยมเล็กๆ เป็น Checkbox
    pdf.rect(15, pdf.get_y()+2, 4, 4); pdf.set_x(22); pdf.cell(40, 8, "โอนย้ายปกติ", 0, 0)
    pdf.rect(55, pdf.get_y()+2, 4, 4); pdf.set_x(62); pdf.cell(40, 8, "ส่งซ่อม/เคลม", 0, 0)
    pdf.rect(95, pdf.get_y()+2, 4, 4); pdf.set_x(102); pdf.cell(40, 8, "ตัดจำหน่าย (Write-off)", 0, 0)
    pdf.rect(145, pdf.get_y()+2, 4, 4); pdf.set_x(152); pdf.cell(40, 8, "อื่นๆ..................", 0, 1)
    pdf.ln(5)

    # --- 3. ตารางรายการอุปกรณ์ (หลายชิ้น) ---
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(10, 10, "ลำดับ", 1, 0, "C", True)
    pdf.cell(50, 10, "Serial Number", 1, 0, "C", True)
    pdf.cell(80, 10, "รายการ/รุ่นอุปกรณ์", 1, 0, "C", True)
    pdf.cell(50, 10, "หมายเหตุ", 1, 1, "C", True)

    pdf.set_font('THSarabun', '', 14)
    # วนลูปสร้างแถว (ในที่นี้ตัวอย่างใส่ไป 5 แถว หรือตาม data['items'])
    items = data.get('items', [(data['sn'], data['model'])]) # ถ้าไม่มีลิสต์ ให้เอาตัวเดียวเดิมมาใส่
    for i, (sn, model) in enumerate(items, 1):
        pdf.cell(10, 10, str(i), 1, 0, "C")
        pdf.cell(50, 10, sn, 1, 0, "C")
        pdf.cell(80, 10, model[:35], 1, 0, "L") # ตัดตัวอักษรถ้าสั้นไป
        pdf.cell(50, 10, "", 1, 1, "C")
    
    pdf.ln(5)
    pdf.set_font('THSarabun', 'B', 12)
    pdf.multi_cell(0, 6, "ข้าพเจ้ายืนยันว่าได้รับ/ส่งมอบอุปกรณ์ในสภาพสมบูรณ์ หากเกิดความเสียหายจากการใช้งานผิดประเภทข้าพเจ้ายินดีรับผิดชอบตามระเบียบของบริษัท", align="C")

    # --- 4. ส่วนลายเซ็น 3 กลุ่ม (กลุ่มละ 2 คน) ---
    pdf.ln(5)
    pdf.set_font('THSarabun', 'B', 11)
    
    # คำนวณความกว้างคอลัมน์ (หาร 3)
    w = 63 

    # หัวข้อกลุ่ม
    pdf.cell(w, 7, "1. ผู้ถือครองเดิม (ต้นทาง)", 0, 0, "C")
    pdf.cell(w, 7, "2. ผู้ถือครองใหม่ (ปลายทาง)", 0, 0, "C")
    pdf.cell(w, 7, "3. ผู้ดำเนินการโยกย้าย", 0, 1, "C")

    # แถวที่ 1: ลายเซ็นพนักงาน
    pdf.ln(10)
    pdf.cell(w, 5, "______________________", 0, 0, "C")
    pdf.cell(w, 5, "______________________", 0, 0, "C")
    pdf.cell(w, 5, "______________________", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w, 5, "( เจ้าของเดิม )", 0, 0, "C")
    pdf.cell(w, 5, "( เจ้าของใหม่ )", 0, 0, "C")
    pdf.cell(w, 5, "( ผู้โยกย้าย )", 0, 1, "C")

    # แถวที่ 2: ลายเซ็นหัวหน้า
    pdf.ln(8)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.cell(w, 5, "______________________", 0, 0, "C")
    pdf.cell(w, 5, "______________________", 0, 0, "C")
    pdf.cell(w, 5, "______________________", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w, 5, "( หัวหน้าต้นทาง )", 0, 0, "C")
    pdf.cell(w, 5, "( หัวหน้าปลายทาง )", 0, 0, "C")
    pdf.cell(w, 5, "( หัวหน้าผู้โยกย้าย )", 0, 1, "C")

    return pdf.output()

# --- UI ส่วนเลือกข้อมูล ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_asset = conn.read(worksheet="Asset Management", ttl="0")

st.title("📦 ระบบออกใบโอนย้ายทรัพย์สิน (Multi-items)")

if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        # เปลี่ยนเป็น multiselect เลือกได้หลายตัว
        selected_sns = st.multiselect("เลือก Serial Number (เลือกได้หลายรายการ)", df_asset["Serial Number (เลขซีเรียล)"].unique())
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

# --- ส่วนการประมวลผล (บรรทัดที่ 145 เป็นต้นไป) ---
if st.button("🚀 เตรียมไฟล์ PDF (Generate)"):
    # ตรวจสอบตัวแปร s_new และ to_location (ต้องตรงกับที่ประกาศไว้ใน UI)
    if not s_new or not to_location:
        st.warning("⚠️ กรุณากรอกชื่อผู้รับและสถานที่ปลายทาง")
    elif not selected_sns:
        st.warning("⚠️ กรุณาเลือก Serial Number อย่างน้อย 1 รายการ")
    else:
        now_th = datetime.now() + timedelta(hours=7)
        
        # เตรียมข้อมูลอุปกรณ์ที่เลือก
        selected_items = []
        for sn in selected_sns:
            # ดึงข้อมูลจาก DataFrame
            row = df_asset[df_asset["Serial Number (เลขซีเรียล)"] == sn].iloc[0]
            selected_items.append({
                "sn": sn,
                "model": row['Model Name (ชื่อรุ่น)']
            })

        # รวบรวมข้อมูลส่งเข้าฟังก์ชันสร้าง PDF
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
            # สร้าง PDF และบันทึกลง Session State
            pdf_out = create_transfer_pdf(pdf_data)
            st.session_state.pdf_ready = bytes(pdf_out)
            st.success(f"✅ เตรียมไฟล์สำหรับอุปกรณ์ {len(selected_sns)} รายการสำเร็จ!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการสร้าง PDF: {e}")

# --- ส่วนปุ่มดาวน์โหลด ---
if st.session_state.pdf_ready is not None:
    st.download_button(
        label="📥 คลิกเพื่อดาวน์โหลด PDF",
        data=st.session_state.pdf_ready,
        file_name=f"Transfer_Note_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
