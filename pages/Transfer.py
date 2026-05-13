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

if st.button("👁️ พรีวิวแบบฟอร์มส่งมอบทรัพย์สิน"):
    now_th = datetime.now() + timedelta(hours=7)
    
    # CSS สำหรับจัดหน้ากระดาษให้เหมือนฟอร์มบริษัท
    st.markdown("""
        <style>
        @media print {
            [data-testid="stSidebar"], [data-testid="stHeader"], .stButton { display: none !important; }
            .main .block-container { padding: 0 !important; margin: 0 !important; }
        }
        .report-paper {
            padding: 40px;
            background-color: white;
            color: black;
            font-family: 'Tahoma', sans-serif;
            border: 1px solid #eee;
            line-height: 1.6;
        }
        .header-table { width: 100%; border: none; }
        .logo-text { color: #1a4a8a; font-weight: bold; font-size: 24px; }
        .company-info { font-size: 12px; text-align: right; }
        .title { text-align: center; font-weight: bold; font-size: 18px; margin: 20px 0; text-decoration: underline; }
        .line-item { border-bottom: 1px solid black; display: inline-block; min-width: 200px; padding-left: 10px; }
        .footer-table { width: 100%; margin-top: 50px; text-align: center; }
        .sig-box { vertical-align: bottom; padding-bottom: 10px; }
        .red-text { color: red; font-weight: bold; text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

    # เนื้อหาฟอร์ม
    html_form = f"""
    <div class="report-paper">
        <!-- Header เหมือนในรูป 576ca1 -->
        <table class="header-table">
            <tr>
                <td class="logo-text">FTS<br><span style="font-size:12px;">กิจการร่วมค้า ฟิวเจอร์ สกาย</span></td>
                <td class="company-info">
                    <b>กิจการร่วมค้า ฟิวเจอร์ สกาย (สำนักงานใหญ่)</b><br>
                    เลขที่ 554/72, 554/73, 554/74 อาคารสกายไลน์ เซ็นเตอร์ ชั้น 15<br>
                    ถนนอโศก-ดินแดง แขวงดินแดง เขตดินแดง กรุงเทพมหานคร 10400
                </td>
            </tr>
        </table>
        <hr style="border: 2px solid black;">
        
        <div class="title">แบบฟอร์มการส่งมอบทรัพย์สินแผนก IT</div>
        
        <div style="text-align: right; margin-bottom: 20px;">
            วันที่ <span class="line-item" style="min-width:150px;">{now_th.strftime('%d/%m/%Y')}</span>
        </div>

        <p>ชื่อ - นามสกุล <span class="line-item" style="width:300px;">{s2}</span> ฝ่าย <span class="line-item" style="width:200px;"></span> แผนก <span class="line-item" style="width:150px;"></span></p>
        <p>เบอร์โทรศัพท์ <span class="line-item" style="width:250px;"></span> สถานที่ทำงาน <span class="line-item" style="width:350px;">{to_location}</span></p>
        
        <div style="margin: 20px 0;">
            <p>☐ Laptop + Mouse + Bag + Adapter &nbsp;&nbsp; <b>หมายเลขเครื่อง :</b> <span class="line-item" style="width:300px;">{target_sn if "Laptop" in asset_info['Model Name (ชื่อรุ่น)'] else ""}</span></p>
            <p>☐ PC Desktop + Monitor + Mouse + Keyboard &nbsp;&nbsp; <b>หมายเลขเครื่อง :</b> <span class="line-item" style="width:300px;">{target_sn if "PC" in asset_info['Model Name (ชื่อรุ่น)'] else ""}</span></p>
            <p>อื่นๆ <span class="line-item" style="width:600px;">{asset_info['Model Name (ชื่อรุ่น)']}</span></p>
        </div>

        <p><b>หมายเหตุ</b> <span class="line-item" style="width:650px;">{transfer_reason}</span></p>
        <div style="border-bottom: 1px solid black; width: 100%; height: 20px;"></div>

        <p style="text-align: center; font-size: 13px; margin-top: 30px;">
            ข้าพเจ้าขอรับรองว่าจะดูแลรักษาอุปกรณ์ที่รับมอบเป็นอย่างดี โดยหากมีความเสียหายใดๆ หรือมีการสูญหายเกิดขึ้น 
            <span class="red-text">ข้าพเจ้าจะขอรับผิดชอบทั้งหมดทุกกรณีโดยไม่มีเงื่อนไข</span> โดยจะทำการซ่อมแซมให้ใช้การได้ดังเดิมหรือจัดหาทดแทนให้ครบในกรณีมีการสูญหายเกิดขึ้น
        </p>
        
        <p style="text-align: center; margin-top: 20px;">จึงเรียนมาเพื่อทราบ และพิจารณาอนุมัติ</p>

        <!-- Signature Section 3 ฝ่าย ตามรูป image_576ca1 -->
        <table class="footer-table">
            <tr>
                <td class="sig-box">ลงชื่อพนักงาน</td>
                <td class="sig-box">ลงชื่อพนักงานฝ่าย IT</td>
                <td class="sig-box">ลงชื่อหัวหน้าฝ่าย IT</td>
            </tr>
            <tr>
                <td style="padding-top: 40px;">__________________________</td>
                <td style="padding-top: 40px;">__________________________</td>
                <td style="padding-top: 40px;">__________________________</td>
            </tr>
            <tr>
                <td>( <span style="display:inline-block; width:150px; border-bottom:1px dotted #ccc;">{s2}</span> )</td>
                <td>( <span style="display:inline-block; width:150px; border-bottom:1px dotted #ccc;">{s1}</span> )</td>
                <td>( <span style="display:inline-block; width:150px; border-bottom:1px dotted #ccc;">{m3}</span> )</td>
            </tr>
            <tr style="font-size: 12px;">
                <td>ส่วนพนักงาน (ผู้รับมอบ)</td>
                <td>ฝ่ายเทคโนโลยีสารสนเทศ</td>
                <td>หัวหน้าฝ่ายเทคโนโลยีสารสนเทศ</td>
            </tr>
            <tr style="font-size: 11px;">
                <td>วันที่ ______/______/______</td>
                <td>วันที่ ______/______/______</td>
                <td>วันที่ ______/______/______</td>
            </tr>
        </table>
    </div>
    """
    st.markdown(html_form, unsafe_allow_html=True)
    st.info("💡 วิธีการใช้งาน: กด Ctrl + P เพื่อพิมพ์ หรือ Save เป็น PDF (หน้าเอกสารจะจัดสัดส่วนให้อัตโนมัติ)")
