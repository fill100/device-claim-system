import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, date

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- ปรับปรุงสีตัวหนังสือและหน้าตา Sidebar เมนูใหม่ ---
st.markdown("""
    <style>
    /* บังคับสีตัวหนังสือในหน้าหลักทั้งหมดให้เข้มขึ้น */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #ffffff; 
    }
    
    /* ซ่อนระบบเมนูนำทางเดิมของ Streamlit เพื่อเลี่ยงบั๊ก */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    
    /* สไตล์สำหรับลิงก์เมนูนำทางแบบกำหนดเอง (Custom Sidebar Menu) */
    .custom-sidebar-link {
        display: block;
        padding: 10px 15px;
        color: #ffffff !important;
        text-decoration: none !important;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 16px;
        transition: background-color 0.2s;
    }
    .custom-sidebar-link:hover {
        background-color: rgba(255,255,255,0.1);
    }
    .sidebar-active {
        background-color: rgba(255,255,255,0.2);
        font-weight: bold;
        border-left: 4px solid #007BFF;
    }
    
    /* ปรับแต่ง Metric Card ให้ตัวเลขและหัวข้อเป็นสีดำเข้ม */
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

# --- 1. เชื่อมต่อฐานข้อมูล ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 2. ข้อมูลตั้งต้น ---
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

# --- 3. Sidebar ---
with st.sidebar:
    st.markdown("# 💻 IT Management")
    
    st.markdown('<a href="/" target="_self" class="custom-sidebar-link sidebar-active">📑 Device Claim</a>', unsafe_allow_html=True)
    st.markdown('<a href="/Wesgan" target="_self" class="custom-sidebar-link">🛡️ Asset System</a>', unsafe_allow_html=True)
    st.markdown('<a href="/Transfer" target="_self" class="custom-sidebar-link">✈️ โอนย้ายของ</a>', unsafe_allow_html=True)
    
    st.divider()
    st.title("🛠️ ตั้งค่าและรายงาน")
    
    with st.expander("🆕 เพิ่มอุปกรณ์ใหม่"):
        new_device = st.text_input("ระบุชื่ออุปกรณ์ใหม่:")
        if st.button("➕ สร้างหน้าใหม่"):
            if new_device and new_device not in st.session_state.available_sheets:
                try:
                    new_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                    conn.update(worksheet=new_device, data=new_df)
                    st.session_state.available_sheets.append(new_device)
                    st.success(f"สร้างหน้า {new_device} สำเร็จ")
                    st.rerun()
                except Exception as e: 
                    st.error(f"สร้างไม่สำเร็จเนื่องจาก: {e}")

    with st.expander("⚠️ ลบอุปกรณ์"):
        target_del = st.selectbox("เลือก Worksheet ที่จะลบ:", st.session_state.available_sheets)
        confirm_delete = st.checkbox(f"ยืนยันลบ '{target_del}'")
        if st.button("🗑️ ยืนยันการลบ"):
            if confirm_delete and len(st.session_state.available_sheets) > 1:
                st.session_state.available_sheets.remove(target_del)
                st.rerun()

    st.divider()
    st.subheader("📊 Export Report")
    if st.button("📦 Prepare All Devices Report"):
        full_report = handle_export_all()
        if full_report is not None:
            st.download_button("✅ Click to Download All", convert_df(full_report), "all_devices.csv", "text/csv")

# --- 4. หน้าหลัก: เลือก Worksheet และ ค้นหา ---
st.title("📑 Claim Management System")

col_ws, col_search = st.columns([1, 2])
with col_ws:
    selected_sheet = st.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)

# ดึงข้อมูลจาก Google Sheets
has_trackmo_col = False
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        if "แก้ในTrackMo" in df.columns: 
            df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
            has_trackmo_col = True
        df = df.astype(str)
        for col in EXPECTED_COLUMNS:
            if col not in df.columns: df[col] = ""
        df = df[EXPECTED_COLUMNS]
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
except Exception:
    df = pd.DataFrame(columns=EXPECTED_COLUMNS)

with col_search:
    q = st.text_input("🔍 ค้นหาข้อมูล:", placeholder="Serial, สาขา, สถานะ...", key="main_search")

# ---
