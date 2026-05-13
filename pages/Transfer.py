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

# --- 3. การแสดงผลเพื่อการพิมพ์ (Print Preview) ---
if st.button("👁️ พรีวิวใบโอนย้าย และพิมพ์เอกสาร"):
    if not to_location or not s1 or not s2:
        st.warning("กรุณากรอกข้อมูลสำคัญ (สถานที่ปลายทาง, ชื่อผู้ส่ง, ชื่อผู้รับ) ให้ครบถ้วน")
    else:
        # สร้างพื้นที่สำหรับ Print
        now_th = datetime.now() + timedelta(hours=7)
        
        # HTML/CSS สำหรับจัดรูปแบบเอกสารให้ดูเหมือนกระดาษ A4
        html_template = f"""
        <div style="padding: 30px; border: 1px solid #ccc; background-color: white; color: black; font-family: 'Tahoma';">
            <div style="text-align: center;">
                <h2 style="margin-bottom: 5px;">ใบโอนย้ายทรัพย์สิน (Asset Transfer Request)</h2>
                <p>วันที่ดำเนินการ: {now_th.strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            <hr>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="padding: 8px;"><b>รหัสซีเรียล (S/N):</b> {target_sn}</td>
                    <td style="padding: 8px;"><b>รุ่น (Model):</b> {asset_info['Model Name (ชื่อรุ่น)']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>สถานที่เดิม:</b> {asset_info['Location (สถานที่)']}</td>
                    <td style="padding: 8px;"><b>สถานที่ปลายทาง:</b> {to_location}</td>
                </tr>
                <tr>
                    <td colspan="2" style="padding: 8px;"><b>เหตุผลการโอนย้าย:</b> {transfer_reason}</td>
                </tr>
            </table>
            
            <table style="width: 100%; margin-top: 50px; text-align: center; border-collapse: collapse;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px; width: 33%;">ฝ่ายต้นทาง (Sender)</th>
                    <th style="border: 1px solid black; padding: 10px; width: 33%;">ฝ่ายปลายทาง (Receiver)</th>
                    <th style="border: 1px solid black; padding: 10px; width: 33%;">ผู้ดำเนินการ (Mover)</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {s1} )<br>เจ้าของเดิม
                    </td>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {s2} )<br>เจ้าของใหม่
                    </td>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {s3} )<br>ผู้ขนย้าย
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {m1} )<br>หัวหน้าฝ่ายต้นทาง
                    </td>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {m2} )<br>หัวหน้าฝ่ายปลายทาง
                    </td>
                    <td style="border: 1px solid black; padding: 40px 10px 10px 10px;">
                        _______________________<br>( {m3} )<br>หัวหน้าฝ่ายขนย้าย
                    </td>
                </tr>
            </table>
            <div style="margin-top: 30px; font-size: 10px; text-align: right; color: #666;">
                <i>เอกสารสร้างโดยระบบ Asset Management System - Audit Reference: {target_sn}-{now_th.strftime('%Y%m%d')}</i>
            </div>
        </div>
        """
        
        st.markdown(html_template, unsafe_allow_html=True)
        st.info("💡 คำแนะนำ: กด Ctrl + P เพื่อพิมพ์เอกสารนี้ หรือบันทึกเป็น PDF")
