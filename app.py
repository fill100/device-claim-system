import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, date
import sys 

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
        st.error(f"เกิดข้อผิดพลาด: {e}")

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
        st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
        
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, label { color: #ffffff; }
    [data-testid="stSidebarNav"] {display: none !important;}
    [data-testid="stSidebarNavItems"] {display: none !important;}
    div[data-testid="stSidebarUserActions"] {display: none !important;}
    .metric-container { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; }
    .metric-card { flex: 1; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 2px solid #444444; }
    .metric-container .metric-card .metric-value { font-size: 36px; font-weight: 900; display: block; color: #000000 !important; }
    .metric-container .metric-card .metric-label { font-size: 18px; font-weight: bold; margin-top: 5px; display: block; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Device Claim"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

INITIAL_SHEETS = ["Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)", "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์", "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"]
if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = INITIAL_SHEETS.copy()

EXPECTED_COLUMNS = ["วันที่รับแจ้ง", "วันทีนำไปติดตั้งใหม่", "สาขา", "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", "สถานะ"]
BRANCH_LIST = ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "กรุงเทพมหานคร 5 (สจก.9)", "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)", "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", "จันทบุรี", "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร", "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง", "ระนอง", "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"]

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

with st.sidebar:
    st.markdown("# 💻 IT Management")
    if st.button("📑 Device Claim", use_container_width=True, type="primary" if st.session_state.current_page == "Device Claim" else "secondary"):
        st.session_state.current_page = "Device Claim"; st.rerun()
    if st.button("🛡️ Asset System", use_container_width=True, type="primary" if st.session_state.current_page == "Asset System" else "secondary"):
        st.session_state.current_page = "Asset System"; st.rerun()
    if st.button("✈️ โอนย้ายของ", use_container_width=True, type="primary" if st.session_state.current_page == "Transfer" else "secondary"):
        st.session_state.current_page = "Transfer"; st.rerun()
    
    if st.session_state.current_page == "Device Claim":
        st.divider()
        st.title("🛠️ ตั้งค่าและรายงาน")
        with st.expander("🆕 เพิ่มอุปกรณ์ใหม่"):
            new_device = st.text_input("ระบุชื่ออุปกรณ์ใหม่:")
            if st.button("➕ สร้างหน้าใหม่"):
                if new_device and new_device not in st.session_state.available_sheets:
                    try:
                        new_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                        conn.update(worksheet=new_device, data=new_df)
                        st.session_state.available_sheets.append(new_device); st.rerun()
                    except Exception as e: st.error(f"สร้างไม่สำเร็จ: {e}")
        with st.expander("⚠️ ลบอุปกรณ์"):
            target_del = st.selectbox("เลือก Worksheet:", st.session_state.available_sheets)
            if st.button("🗑️ ยืนยันการลบ"):
                if len(st.session_state.available_sheets) > 1:
                    st.session_state.available_sheets.remove(target_del); st.rerun()
        st.divider()
        st.subheader("📊 Export Report")
        if st.button("📦 Prepare All Devices Report"):
            full_report = handle_export_all()
            if full_report is not None: st.download_button("✅ Download All", convert_df(full_report), "all_devices.csv", "text/csv")

# --- โครงสร้าง Routing ที่ถูกต้อง ---
if st.session_state.current_page == "Asset System":
    show_asset_system(conn)
elif st.session_state.current_page == "Transfer":
    show_transfer_system(conn)
else:
    # (วางโค้ดหน้า Device Claim ของคุณต่อที่นี่ได้เลยครับ)
    st.write("เลือกเมนู Device Claim เพื่อเริ่มใช้งาน")
