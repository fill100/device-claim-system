import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import io

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- ปรับปรุงสีและ CSS (เน้นความชัดเจน) ---
st.markdown("""
    <style>
    /* ปรับสีตัวหนังสือหลักให้เข้มชัดเจน */
    html, body, [class*="css"] {
        color: #1A1A1A !important; 
    }
    
    /* ซ่อนเมนูเดิม */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    
    /* ปรับแต่ง Metric Card ให้สีเข้มและชัดเจน */
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        display: block;
    }
    .metric-label {
        font-size: 16px;
        margin-top: 5px;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. เชื่อมต่อฐานข้อมูล ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 2. ข้อมูลตั้งต้น (ข้อมูลครบถ้วนตามเดิม) ---
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

# --- 3. Sidebar: ระบบจัดการ ---
with st.sidebar:
    st.markdown("### 🛠️ ตั้งค่าระบบ")
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

    st.divider()
    if st.button("📦 Prepare All Devices Report"):
        # (ฟังก์ชันดึงทุก Sheet รวมกัน)
        st.info("กำลังประมวลผล...")

# --- 4. ส่วนค้นหาและเลือก Worksheet (เน้น UI ชัดเจน) ---
st.title("📑 Claim Management System")

search_row1, search_row2 = st.columns([1, 2])
with search_row1:
    selected_sheet = st.selectbox("📂 เลือกประเภทอุปกรณ์ (Worksheet):", st.session_state.available_sheets)

# ดึงข้อมูล
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        df = df.astype(str)
        for col in EXPECTED_COLUMNS:
            if col not in df.columns: df[col] = ""
        df = df[EXPECTED_COLUMNS]
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
except Exception:
    df = pd.DataFrame(columns=EXPECTED_COLUMNS)

with search_row2:
    q = st.text_input("🔍 ค้นหาข้อมูลในตาราง:", placeholder="พิมพ์ Serial, สาขา หรือสถานะที่นี่...")

# --- 5. Dashboard Metrics (ปรับสีใหม่ให้เข้มและชัด) ---
status_col = df["สถานะ"].str.strip().str.lower()
inprogress = len(df[status_col == "inprogress"])
done = len(df[status_col == "done"])

st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card" style="background-color: #E3F2FD; border: 2px solid #2196F3;">
            <span class="metric-label" style="color: #0D47A1;">ทั้งหมดในหน้านี้</span>
            <span class="metric-value" style="color: #0D47A1;">{len(df)}</span>
        </div>
        <div class="metric-card" style="background-color: #FFFDE7; border: 2px solid #FBC02D;">
            <span class="metric-label" style="color: #827717;">In Progress (กำลังซ่อม)</span>
            <span class="metric-value" style="color: #827717;">{inprogress}</span>
        </div>
        <div class="metric-card" style="background-color: #E8F5E9; border: 2px solid #4CAF50;">
            <span class="metric-label" style="color: #1B5E20;">Done (เสร็จสิ้น)</span>
            <span class="metric-value" style="color: #1B5E20;">{done}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. แบบฟอร์มเพิ่ม/แก้ไข (ย่อไว้เพื่อให้หน้าจอไม่รก) ---
with st.expander("➕ เพิ่มรายการแจ้งซ่อมใหม่", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            br = st.selectbox("สาขา", BRANCH_LIST)
            cnt = st.text_input("Counter")
            sn_f = st.text_input("Serial เครื่องเสีย (จำเป็น)")
        with f2:
            stt = st.selectbox("สถานะ", ["inprogress", "Done"])
            dt_clm = st.date_input("วันทีนำไปติดตั้งใหม่", value=None)
            sn_n = st.text_input("Serial เครื่องที่ส่งให้ศูนย์")
        
        if st.form_submit_button("💾 บันทึกข้อมูลใหม่"):
            if sn_f:
                now_thailand = datetime.now() + timedelta(hours=7)
                time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": time_str, "วันทีนำไปติดตั้งใหม่": dt_clm.strftime("%Y-%m-%d") if dt_clm else "",
                    "สาขา": br, "counter": cnt, "Serial เครื่องที่เสีย": sn_f, "สถานะ": stt, 
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_n
                }])
                df = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet=selected_sheet, data=df)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# --- 7. ตารางข้อมูล (เน้นเส้นขอบและตัวหนังสือดำ) ---
st.divider()
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]

st.markdown(f"**แสดงข้อมูลอุปกรณ์:** `{selected_sheet}` | **พบทั้งหมด:** `{len(view)}` รายการ")

# ใช้ st.dataframe แบบปรับแต่ง
st.dataframe(
    view, 
    use_container_width=True, 
    hide_index=True
)

# ปุ่มดาวน์โหลด
if not view.empty:
    st.download_button(
        label=f"📥 ดาวน์โหลดข้อมูล {selected_sheet} (CSV)",
        data=convert_df(view),
        file_name=f"{selected_sheet}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
