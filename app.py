import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, date

# --- ตั้งค่าหน้ากระดาษหลัก ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- สไตล์ปรับแต่งหน้าตา UI ดั้งเดิมของคุณ ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #ffffff; 
    }
    /* ซ่อนเมนูอัตโนมัติของ Streamlit */
    [data-testid="stSidebarNav"] {display: none !important;}
    [data-testid="stSidebarNavItems"] {display: none !important;}
    div[data-testid="stSidebarUserActions"] {display: none !important;}
    
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        flex: 1;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 2px solid #444444;
    }
    .metric-container .metric-card .metric-value {
        font-size: 36px;
        font-weight: 900; 
        display: block;
        color: #000000 !important; 
    }
    .metric-container .metric-card .metric-label {
        font-size: 18px;
        font-weight: bold;
        margin-top: 5px;
        display: block;
        color: #000000 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบจัดเก็บสถานะหน้าปัจจุบัน (State Control) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Device Claim"

# --- 1. เชื่อมต่อฐานข้อมูลหลัก ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 2. ข้อมูลตั้งต้นระบบคลังชีต ---
INITIAL_SHEETS = [
    "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = INITIAL_SHEETS.copy()

EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", "สถานะ"
]

BRANCH_LIST = [
    "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "กรุงเทพมหานคร 5 (สจก.9)", 
    "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)", "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", 
    "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", 
    "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", 
    "จันทบุรี", "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร", 
    "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", 
    "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง", "ระนอง", 
    "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", 
    "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"
]

def convert_df(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8-sig')

def handle_export_all():
    all_data = []
    for sheet in st.session_state.available_sheets:
        try:
            temp_df = conn.read(worksheet=sheet, ttl="0")
            if temp_df is not None and not temp_df.empty:
                temp_df.columns = temp_df.columns.str.strip()
                if "แก้ในTrackMo" in temp_df.columns: 
                    temp_df = temp_df.rename(columns={"แก้ในTrackMo": "สถานะ"})
                temp_df["ประเภทอุปกรณ์"] = sheet
                all_data.append(temp_df)
        except: continue
    return pd.concat(all_data, ignore_index=True) if all_data else None

# --- 3. Sidebar (เปลี่ยนไปใช้ st.button นำทาง เพื่อแก้จุดบกพร่องเรื่องจอดำทั้งหมด) ---
with st.sidebar:
    st.markdown("# 💻 IT Management")
    
    if st.button("📑 Device Claim", use_container_width=True, type="primary" if st.session_state.current_page == "Device Claim" else "secondary"):
        st.session_state.current_page = "Device Claim"
        st.rerun()
        
    if st.button("🛡️ Asset System", use_container_width=True, type="primary" if st.session_state.current_page == "Asset System" else "secondary"):
        st.session_state.current_page = "Asset System"
        st.rerun()
        
    if st.button("✈️ โอนย้ายของ", use_container_width=True, type="primary" if st.session_state.current_page == "Transfer" else "secondary"):
        st.session_state.current_page = "Transfer"
        st.rerun()
    
    # ซ่อนเมนูข้อ 2 อัตโนมัติเมื่อย้ายหน้าตามที่คุณต้องการ
    if st.session_state.current_page == "Device Claim":
        st.divider()
        st.title("🛠️ ตั้งค่าและรายงาน")
        
        with st.expander("🆕 เพิ่มอุปกรณ์ใหม่"):
            new_device = st.text_input("ระบุชื่ออุปกรณ์ใหม่:")
            if st.button("➕ สร้างหน้าใหม่"):
