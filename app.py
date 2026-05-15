import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import io

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- ปรับแต่งสี (CSS) ให้มองเห็นชัดเจน (High Contrast) ---
st.markdown("""
    <style>
    /* เน้นตัวหนังสือในหน้าเว็บทั้งหมดให้เป็นสีดำเข้ม */
    html, body, [class*="css"], .stMarkdown, p, span {
        color: #000000 !important;
    }
    
    /* ซ่อนเมนูเดิม */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    
    /* ปรับแต่ง Metric Card ให้สีเข้มและมีเส้นขอบชัดเจน */
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
        border: 2px solid #333333;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        display: block;
        color: #000000 !important;
    }
    .metric-label {
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

# --- 2. ข้อมูลตั้งต้น (ครบถ้วนตามต้นฉบับ) ---
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

# ฟังก์ชัน Export
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

# --- 3. Sidebar: Navigation & Config ---
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

    # ส่วนลบอุปกรณ์
    with st.expander("⚠️ ลบอุปกรณ์"):
        # ใน Sidebar เราจะให้เลือก Worksheet ที่จะลบจากลิสต์ที่มี
        target_del = st.selectbox("เลือก Worksheet ที่จะลบ:", st.session_state.available_sheets, key="del_box")
        confirm_delete = st.checkbox(f"ยืนยันลบ '{target_del}'")
        if st.button("🗑️ ยืนยันการลบ"):
            if confirm_delete and len(st.session_state.available_sheets) > 1:
                st.session_state.available_sheets.remove(target_del)
                st.success(f"ลบ {target_del} สำเร็จ")
                st.rerun()

    st.divider()
    st.subheader("📊 Export Report")
    if st.button("📦 Prepare All Devices Report"):
        full_report = handle_export_all()
        if full_report is not None:
            st.download_button("✅ Click to Download All", convert_df(full_report), "all_devices.csv", "text/csv")

# --- 4. ส่วนหน้าหลัก: ค้นหาและเลือก Worksheet (ปรับปรุงสีและตำแหน่ง) ---
st.title("📑 Claim Management System")

# แถวสำหรับเลือก Worksheet และ ค้นหา
search_row1, search_row2 = st.columns([1, 2])

with search_row1:
    selected_sheet = st.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)

# --- 5. ดึงข้อมูล (ดึงตาม Worksheet ที่เลือก) ---
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

with search_row2:
    q = st.text_input("🔍 ค้นหาข้อมูล:", placeholder="Serial, สาขา, สถานะ...", key="main_search")

# --- 6. Dashboard Metrics (ปรับสีเข้ม High Contrast) ---
status_col = df["สถานะ"].str.strip().str.lower()
inprogress = len(df[status_col == "inprogress"])
done = len(df[status_col == "done"])

st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card" style="background-color: #CCE5FF; border-color: #004085;">
            <span class="metric-label">ทั้งหมดในหน้านี้</span>
            <span class="metric-value">{len(df)}</span>
        </div>
        <div class="metric-card" style="background-color: #FFF3CD; border-color: #856404;">
            <span class="metric-label">In Progress (กำลังซ่อม)</span>
            <span class="metric-value">{inprogress}</span>
        </div>
        <div class="metric-card" style="background-color: #D4EDDA; border-color: #155724;">
            <span class="metric-label">Done (เสร็จสิ้น)</span>
            <span class="metric-value">{done}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. เพิ่มรายการใหม่ (คงเดิมทุกอย่าง) ---
with st.expander("➕ เพิ่มรายการแจ้งซ่อม"):
    with st.form("add_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            br = st.selectbox("สาขา", BRANCH_LIST)
            cnt = st.text_input("Counter")
            sn_f = st.text_input("Serial เครื่องเสีย (บังคับ)")
        with f2:
            stt = st.selectbox("สถานะ", ["inprogress", "Done"])
            dt_clm = st.date_input("วันทีนำไปติดตั้งใหม่", value=None)
            sn_n = st.text_input("Serial เครื่องเปลี่ยนใหม่")
        
        submit_btn = st.form_submit_button("บันทึกข้อมูล")
        if submit_btn:
            if sn_f:
                now_thailand = datetime.now() + timedelta(hours=7)
                time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": time_str, 
                    "วันทีนำไปติดตั้งใหม่": dt_clm.strftime("%Y-%m-%d") if dt_clm else "", 
                    "สาขา": br, 
                    "counter": cnt, 
                    "Serial เครื่องที่เสีย": sn_f, 
                    "สถานะ": stt, 
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_n
                }])
                df = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet=selected_sheet, data=df)
                st.success(f"บันทึกข้อมูลสำเร็จเมื่อเวลา {time_str}")
                st.rerun()
            else:
                st.error("กรุณาระบุ Serial เครื่องที่เสีย")

# --- 8. แก้ไขและลบแถว (คงเดิมทุกอย่าง) ---
if not df.empty:
    with st.expander("📝 แก้ไข หรือ ลบรายการ"):
        sn_list = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial ที่ต้องการจัดการ:", sn_list)
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        row = df.loc[idx]

        with st.form("edit_full_form"):
            e1, e2, e3 = st.columns(3)
            with e1:
                new_d_rec = st.text_input("วันที่รับแจ้ง", value=str(row["วันที่รับแจ้ง"]))
                try: curr_d_ins = datetime.strptime(str(row["วันทีนำไปติดตั้งใหม่"]), "%Y-%m-%d")
                except: curr_d_ins = None
                new_d_ins = st.date_input("วันทีนำไปติดตั้งใหม่", value=curr_d_ins)
                new_s = st.selectbox("สถานะ", ["inprogress", "Done"], index=0 if str(row["สถานะ"]).lower() == "inprogress" else 1)
            with e2:
                new_b = st.selectbox("สาขา", BRANCH_LIST, index=BRANCH_LIST.index(str(row["สาขา"])) if str(row["สาขา"]) in BRANCH_LIST else 0)
                new_c = st.text_input("Counter", value=str(row["counter"]))
            with e3:
                new_sn_f = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))
                new_sn_ctr = st.text_input("Serial เครื่องที่ส่งให้ศูนย์", value=str(row["Serial เครื่องที่ส่งให้ศูนย์"]))
            
            st.divider()
            b1, b2 = st.columns(2)
            if b1.form_submit_button("💾 บันทึกการแก้ไขทั้งหมด"):
                df = df.astype(object)
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec
                df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                df.at[idx, "สถานะ"] = new_s
                conn.update(worksheet=selected_sheet, data=df.astype(str))
                st.success("อัปเดตข้อมูลสำเร็จ!")
                st.rerun()
            if b2.form_submit_button("🗑️ ลบรายการนี้ออก"):
                df_dropped = df.drop(idx)
                conn.update(worksheet=selected_sheet, data=df_dropped.astype(str))
                st.warning(f"ลบรายการ {sel_sn} ออกแล้ว")
                st.rerun()

# --- 9. ตารางค้นหา ---
st.divider()
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]

st.markdown(f"**แสดงข้อมูล:** `{selected_sheet}` | **พบ:** `{len(view)}` รายการ")
st.dataframe(view, use_container_width=True, hide_index=True)

if not view.empty:
    st.download_button(f"📥 Download {selected_sheet} (CSV)", convert_df(view), f"{selected_sheet}.csv", "text/csv")
