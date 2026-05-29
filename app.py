import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- ปรับปรุงสีตัวหนังสือให้ชัดเจนที่สุด (High Contrast) ---
st.markdown("""
    <style>
    /* บังคับสีตัวหนังสือในหน้าหลักทั้งหมดให้เข้มขึ้น */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #ffffff !important; /* สีขาวสำหรับข้อความทั่วไปบนพื้นหลังมืด */
    }
    
    /* ซ่อนเมนูเดิม */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    
    /* ปรับแต่ง Metric Card ให้ตัวเลขและหัวข้อเป็นสีดำเข้ม (เพื่อให้อ่านออกบนพื้นสีสว่าง) */
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
    .metric-value {
        font-size: 36px;
        font-weight: 900; /* หนาพิเศษ */
        display: block;
        color: #000000 !important; /* บังคับเป็นสีดำ */
    }
    .metric-label {
        font-size: 18px;
        font-weight: bold;
        margin-top: 5px;
        display: block;
        color: #000000 !important; /* บังคับเป็นสีดำ */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. เชื่อมต่อฐานข้อมูล ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 2. ข้อมูลตั้งต้น (ครบถ้วนตามเดิม) ---
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
                temp_df["ประเภทอุปกรณ์"] = sheet
                all_data.append(temp_df)
        except: continue
    return pd.concat(all_data, ignore_index=True) if all_data else None

# --- 3. Sidebar ---
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.page_link("pages/Transfer.py", label="โอนย้ายของ", icon="✈️")
    st.divider()
    st.title("🛠️ ตั้งค่าและรายงาน")
    
    with st.expander("🆕 เพิ่มอุปกรณ์ใหม่"):
        new_device = st.text_input("ระบุชื่ออุปกรณ์ใหม่:")
        if st.button("➕ สร้างหน้าใหม่"):
            if new_device and new_device not in st.session_state.available_sheets:
                try:
                    new_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                    conn.create(worksheet=new_device, data=new_df)
                    st.session_state.available_sheets.append(new_device)
                    st.rerun()
                except: st.error("สร้างไม่สำเร็จ")

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

# ดึงข้อมูล
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        if "แก้ในTrackMo" in df.columns: df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
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

# --- 5. Dashboard Metrics ---
status_col = df["สถานะ"].str.strip().str.lower()
inprogress = len(df[status_col == "inprogress"])
done = len(df[status_col == "done"])

st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card" style="background-color: #D1E9FF; border-color: #007BFF;">
            <span class="metric-label">ทั้งหมดในหน้านี้</span>
            <span class="metric-value">{len(df)}</span>
        </div>
        <div class="metric-card" style="background-color: #FFF9C4; border-color: #FBC02D;">
            <span class="metric-label">In Progress (กำลังซ่อม)</span>
            <span class="metric-value">{inprogress}</span>
        </div>
        <div class="metric-card" style="background-color: #C8E6C9; border-color: #388E3C;">
            <span class="metric-label">Done (เสร็จสิ้น)</span>
            <span class="metric-value">{done}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. ส่วนฟอร์มเพิ่มข้อมูล (Bulk Insert) ---
with st
