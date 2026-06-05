import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, date
import sys

# --- ฟังก์ชันโหลดไฟล์ภายนอก ---
def show_asset_system(conn):
    try:
        with open("Wesgan.py", encoding="utf-8") as f:
            code = f.read()
            ns = {}
            exec(code, ns)
            if 'main' in ns:
                ns['main'](conn)
            else:
                st.error("ไม่พบฟังก์ชัน 'main' ในไฟล์ Wesgan.py")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลด Asset System: {e}")

def show_transfer_system(conn):
    try:
        with open("Transfer.py", encoding="utf-8") as f:
            code = f.read()
            ns = {}
            exec(code, ns)
            if 'run_transfer_page' in ns:
                ns['run_transfer_page'](conn)
            else:
                st.error("ไม่พบฟังก์ชัน 'run_transfer_page' ในไฟล์ Transfer.py")
    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลด Transfer System: {e}")

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    html, body, .stMarkdown, p, span, label { color: #ffffff; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .metric-card { padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 2px solid #444444; }
    .metric-value { font-size: 36px; font-weight: 900; color: #000000 !important; }
    .metric-label { font-size: 18px; font-weight: bold; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Initial States ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Device Claim"

INITIAL_SHEETS = ["Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)", "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์", "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"]
if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = INITIAL_SHEETS.copy()

EXPECTED_COLUMNS = ["วันที่รับแจ้ง", "วันทีนำไปติดตั้งใหม่", "สาขา", "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", "สถานะ"]
BRANCH_LIST = ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ระยอง", "ตราด", "จันทบุรี", "สระแก้ว", "ขอนแก่น", "นครราชสีมา", "หนองคาย", "มุกดาหาร", "อุบลราชธานี", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "ระนอง", "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"]

# --- เชื่อมต่อฐานข้อมูล ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Sidebar (เมนู) ---
with st.sidebar:
    st.markdown("# 💻 IT Management")
    if st.button("📑 Device Claim", use_container_width=True):
        st.session_state.current_page = "Device Claim"
        st.rerun()
    if st.button("🛡️ Asset System", use_container_width=True):
        st.session_state.current_page = "Asset System"
        st.rerun()
    if st.button("✈️ โอนย้ายของ", use_container_width=True):
        st.session_state.current_page = "Transfer"
        st.rerun()

    # แสดงเมนูตั้งค่าเฉพาะหน้า Device Claim
    if st.session_state.current_page == "Device Claim":
        st.divider()
        st.title("🛠️ ตั้งค่าและรายงาน")
        # (เพิ่มฟังก์ชันจัดการ Sheet ของคุณตรงนี้ได้เลย)

# --- Routing Main Content ---
if st.session_state.current_page == "Asset System":
    show_asset_system(conn)
elif st.session_state.current_page == "Transfer":
    show_transfer_system(conn)
else:
    # --- หน้าหลัก Device Claim ---
    st.title("📑 Claim Management System")
    selected_sheet = st.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)
    
    # อ่านข้อมูล
    try:
        df = conn.read(worksheet=selected_sheet, ttl="0")
        if df is not None:
            df.columns = df.columns.str.strip()
            if "แก้ในTrackMo" in df.columns: df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
            df = df.astype(str)
        else:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    except:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

    # แสดงผลตาราง (ใส่โค้ดส่วนตารางและการจัดการข้อมูลของคุณที่นี่)
    st.dataframe(df, use_container_width=True)
