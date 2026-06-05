import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os
import io

# --- 1. ตั้งค่าหน้ากระดาษ (ทำครั้งเดียวที่บนสุดของไฟล์) ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- 2. ปรับปรุงสไตล์และซ่อนเมนูนำทางอัตโนมัติของระบบเก่า ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] {display: none !important;}
    [data-testid="stSidebarNavItems"] {display: none !important;}
    
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
        font-weight: 900;
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

# --- 3. ตัวแปรควบคุมหน้าเว็บ (สลับหน้าด้วย Session State) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Device Claim"

# --- 4. เชื่อมต่อฐานข้อมูลหลัก ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 5. ฟังก์ชันสำหรับสร้างใบโอนย้ายทรัพย์สิน (PDF) ---
def create_transfer_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "FTS-LOGO-01.png")
    font_path = os.path.join(current_dir, "THSarabunNew.ttf")

    # Header (Logo + Address)
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
    
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.6)
    pdf.line(10, 35, 200, 35) 
    
    pdf.ln(12)
    pdf.set_font('THSarabun', 'B', 18)
    pdf.cell(0, 10, "แบบฟอร์มการส่งมอบและโยกย้ายทรัพย์สิน", 0, 1, "C")
    
    pdf.set_font('THSarabun', '', 14)
    pdf.cell(0, 8, f"วันที่ดำเนินการ: {data['date']}", 0, 1, "R")
    pdf.cell(0, 8, f"สถานที่ปลายทาง: {data['to_loc']}", 0, 1, "L")
    pdf.ln(2)

    # ส่วน Checkbox ประเภทการดำเนินการ
    pdf.set_font('THSarabun', 'B', 14)
    pdf.cell(0, 8, "ประเภทการดำเนินการ:", 0, 1)
    pdf.set_line_width(0.2)
    pdf.set_font('THSarabun', '', 14)
    
    types_list = ["โอนย้ายปกติ", "ส่งซ่อม/เคลม", "ตัดจำหน่าย", "อื่นๆ"]
    x_pos = [15, 55, 95, 135]
    
    for i, t_name in enumerate(types_list):
        pdf.rect(x_pos[i], pdf.get_y()+2, 4, 4)
        if data['transfer_type'] == t_name:
            pdf.set_font('Arial', 'B', 10)
            pdf.text(x_pos[i]+0.8, pdf.get_y()+5.2, "X")
            pdf.set_font('THSarabun', '', 14)
        
        pdf.set_x(x_pos[i]+7)
        display_name = t_name if t_name != "อื่นๆ" else "อื่นๆ............................."
        pdf.cell(40, 8, display_name, 0, 0)
    pdf.ln(10)

    # ตารางรายการทรัพย์สิน
    pdf.set_font('THSarabun', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    w_no, w_asset, w_note = 15, 80, 95
    h_cell = 10

    pdf.cell(w_no, h_cell, "ลำดับ", 1, 0, "C", True)
    pdf.cell(w_asset, h_cell, "เลขทรัพย์สิน / รายการอุปกรณ์", 1, 0, "C", True)
    pdf.cell(w_note, h_cell, "หมายเหตุรายรายการ", 1, 1, "C", True)

    pdf.set_font('THSarabun', '', 14)
    for i, row in enumerate(data['items'], 1):
        asset_val = str(row.get("เลขทรัพย์สิน/ชื่อรายการ", ""))
        note_val = str(row.get("หมายเหตุ", ""))
        pdf.cell(w_no, h_cell, str(i), 1, 0, "C")
        pdf.cell(w_asset, h_cell, f" {asset_val}", 1, 0, "L")
        pdf.cell(w_note, h_cell, f" {note_val}", 1, 1, "L")
    
    # Footer & ลายเซ็น
    pdf.ln(7)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.multi_cell(0, 6, "ข้าพเจ้ายืนยันว่าได้รับ/ส่งมอบอุปกรณ์ข้างต้นในสภาพสมบูรณ์ หากเกิดความเสียหายจากการใช้งานผิดประเภทข้าพเจ้ายินดีรับผิดชอบตามระเบียบของบริษัท", align="C")

    pdf.ln(5)
    w_sign = 63.3
    pdf.set_font('THSarabun', 'B', 11)
    pdf.cell(w_sign, 7, "1. ผู้ถือครองเดิม (ต้นทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "2. ผู้ถือครองใหม่ (ปลายทาง)", 0, 0, "C")
    pdf.cell(w_sign, 7, "3. ผู้ดำเนินการโยกย้าย", 0, 1, "C")
    pdf.ln(10)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, f"( {data['s_old']} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data['s_new']} )", 0, 0, "C")
    pdf.cell(w_sign, 5, f"( {data['it_staff']} )", 0, 1, "C")
    pdf.ln(8)
    pdf.set_font('THSarabun', 'B', 11)
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 0, "C")
    pdf.cell(w_sign, 5, "______________________", 0, 1, "C")
    pdf.set_font('THSarabun', '', 10)
    pdf.cell(w_sign, 5, "( หัวหน้าต้นทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าปลายทาง )", 0, 0, "C")
    pdf.cell(w_sign, 5, "( หัวหน้าฝ่าย IT )", 0, 1, "C")

    return pdf.output()

# --- 6. Sidebar Menu (ปุ่มกดสลับหน้าแบบหน้าเดียวที่ปลอดภัยที่สุด) ---
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

# ==========================================
# 🟢 หน้าที่ 1: DEVICE CLAIM
# ==========================================
if st.session_state.current_page == "Device Claim":
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

    # เมนูการตั้งค่าใน Sidebar ของหน้า Device Claim
    with st.sidebar:
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

    st.title("📑 Claim Management System")
    col_ws, col_search = st.columns([1, 2])
    with col_ws:
        selected_sheet = st.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)

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
            
            if st.form_submit_button("บันทึกข้อมูล"):
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
                    st.success("บันทึกข้อมูลสำเร็จ!")
                    st.rerun()

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
                if st.form_submit_button("💾 บันทึกการแก้ไข"):
                    df = df.astype(object)
                    df.at[idx, "วันที่รับแจ้ง"] = new_d_rec
                    df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                    df.at[idx, "สาขา"] = new_b
                    df.at[idx, "counter"] = new_c
                    df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                    df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                    df.at[idx, "สถานะ"] = new_s
                    conn.update(worksheet=selected_sheet, data=df.astype(str))
                    st.success("อัปเดตเรียบร้อย!")
                    st.rerun()

    st.divider()
    view = df.copy()
    if q:
        mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True)

# ==========================================
# 🔵 หน้าที่ 2: ASSET SYSTEM
# ==========================================
elif st.session_state.current_page == "Asset System":
    st.title("🛡️ Asset Management")
    
    # --- กำหนดโครงสร้างข้อมูล ---
    ASSET_COLUMNS = ["Serial Number (เลขซีเรียล)", "Model Name (ชื่อรุ่น)", "Location (สถานที่)", "วันที่ซื้อ"]

    # --- ดึงข้อมูล ---
    try:
        df_asset = conn.read(worksheet="Asset Management", ttl="0")
        if df_asset is not None and not df_asset.empty:
            df_asset.columns = df_asset.columns.str.strip()
            for col in ASSET_COLUMNS:
                if col not in df_asset.columns: df_asset[col] = ""
            df_asset = df_asset[ASSET_COLUMNS]
        else:
            df_asset = pd.DataFrame(columns=ASSET_COLUMNS)
    except:
        df_asset = pd.DataFrame(columns=ASSET_COLUMNS)

    # --- จัดการ State สำหรับการแก้ไข ---
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = None
    if "row_index" not in st.session_state:
        st.session_state.row_index = None

    def reset_edit_state():
        st.session_state.edit_data = None
        st.session_state.row_index = None

    # --- Sidebar Filters เจาะจงเฉพาะหน้านี้ ---
    with st.sidebar:
        st.divider()
        st.subheader("🎯 ตัวกรอง Model")
        all_models = ["ทั้งหมด"] + sorted(df_asset["Model Name (ชื่อรุ่น)"].unique().tolist())
        filter_model = st.selectbox("เลือกดูเฉพาะรุ่น:", all_models)

    # กรองข้อมูลตามโมเดล
    view_df = df_asset.copy()
    if filter_model != "ทั้งหมด":
        view_df = view_df[view_df["Model Name (ชื่อรุ่น)"] == filter_model]

    # --- ฟอร์ม ลงทะเบียน/แก้ไข ---
    is_editing = st.session_state.edit_data is not None
    expander_label = "📝 แก้ไขข้อมูลทรัพย์สิน" if is_editing else "➕ ลงทะเบียนทรัพย์สินใหม่"

    with st.expander(expander_label, expanded=is_editing):
        with st.form("asset_form", clear_on_submit=True):
            current_val = st.session_state.edit_data if is_editing else {}
            
            col1, col2 = st.columns(2)
            with col1:
                input_sn = st.text_input("Serial Number", value=current_val.get("Serial Number (เลขซีเรียล)", ""))
                input_model = st.text_input("Model Name", value=current_val.get("Model Name (ชื่อรุ่น)", ""))
            with col2:
                input_loc = st.text_input("Location", value=current_val.get("Location (สถานที่)", ""))
                
                try:
                    if is_editing and current_val.get("วันที่ซื้อ"):
                        default_date = datetime.strptime(current_val.get("วันที่ซื้อ"), "%d-%m-%Y")
                    else:
                        default_date = datetime.now()
                except:
                    default_date = datetime.now()
                
                input_date = st.date_input("วันที่ซื้อ", value=default_date, format="DD/MM/YYYY")
            
            b_col1, b_col2 = st.columns([1, 5])
            with b_col1:
                submit = st.form_submit_button("💾 บันทึก")
            with b_col2:
                if is_editing:
                    if st.form_submit_button("❌ ยกเลิกการแก้ไข"):
                        reset_edit_state()
                        st.rerun()

            if submit:
                if input_sn:
                    updated_row_data = {
                        "Serial Number (เลขซีเรียล)": str(input_sn),
                        "Model Name (ชื่อรุ่น)": str(input_model),
                        "Location (สถานที่)": str(input_loc),
                        "วันที่ซื้อ": input_date.strftime("%d-%m-%Y"),
                    }
                    
                    try:
                        if is_editing:
                            df_asset.iloc[st.session_state.row_index] = updated_row_data
                            success_msg = "อัปเดตข้อมูลเรียบร้อยแล้ว!"
                        else:
                            new_row_df = pd.DataFrame([updated_row_data])
                            df_asset = pd.concat([df_asset, new_row_df], ignore_index=True)
                            success_msg = "ลงทะเบียนใหม่เรียบร้อยแล้ว!"
                        
                        conn.update(worksheet="Asset Management", data=df_asset.astype(str))
                        st.success(success_msg)
                        reset_edit_state()
                        st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
                else:
                    st.error("กรุณาระบุ Serial Number")

    # --- ส่วนแสดงผลตารางและรายงาน ---
    st.divider()
    c1, c2 = st.columns([3, 1])

    with c1:
        search_term = st.text_input("🔍 ค้นหาในตาราง (S/N, รุ่น, สถานที่):")
        if search_term:
            mask = view_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            view_df = view_df[mask]

    with c2:
        st.write("📊 Report")
        csv_data = view_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"Asset_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.write(f"พบข้อมูลทั้งหมด: **{len(view_df)}** รายการ (คลิกที่ช่องสถานที่เพื่อแก้ไขได้ทันที)")

    edited_view_df = st.data_editor(
        view_df,
        use_container_width=True,
        hide_index=False,
        column_config={
            "Serial Number (เลขซีเรียล)": st.column_config.TextColumn(disabled=True),
            "Model Name (ชื่อรุ่น)": st.column_config.TextColumn(disabled=True),
            "วันที่ซื้อ": st.column_config.TextColumn(disabled=True),
            "Location (สถานที่)": st.column_config.TextColumn(disabled=False)
        },
        key="bulk_edit_location"
    )

    if st.button("✅ ยืนยันการเปลี่ยนสถานที่ในตาราง"):
        try:
            df_asset.update(edited_view_df)
            conn.update(worksheet="Asset Management", data=df_asset.astype(str))
            st.success("บันทึกการเปลี่ยนสถานที่เรียบร้อย!")
            st.rerun()
        except Exception as e:
            st.error(f"ไม่สามารถบันทึกได้: {e}")

# ==========================================
# 🔴 หน้าที่ 3: โอนย้ายของ (TRANSFER SYSTEM)
# ==========================================
elif st.session_state.current_page == "Transfer":
    st.title("📦 ระบบพิมพ์ใบโอนย้ายทรัพย์สิน")

    if "df_data" not in st.session_state:
        st.session_state.df_data = pd.DataFrame([{"เลขทรัพย์สิน/ชื่อรายการ": "", "หมายเหตุ": ""}])

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            transfer_type = st.radio("**ประเภทการดำเนินการ**", ["โอนย้ายปกติ", "ส่งซ่อม/เคลม", "ตัดจำหน่าย", "อื่นๆ"], horizontal=True)
            st.write("---")
            st.write("**รายการทรัพย์สิน**")
            edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
        with col2:
            st.write("**ข้อมูลผู้ดำเนินการ**")
            to_location = st.text_input("สถานที่ปลายทาง")
            s_old = st.text_input("ชื่อผู้ถือครองเดิม")
            s_new = st.text_input("ชื่อผู้ถือครองใหม่")
            it_staff = st.text_input("ชื่อผู้ดำเนินการ (IT)")

    if st.button("🚀 Generate PDF"):
        clean_items = edited_df[edited_df["เลขทรัพย์สิน/ชื่อรายการ"].str.strip() != ""].to_dict('records')
        if not clean_items or not to_location:
            st.error("⚠️ กรุณากรอกรายการและสถานที่ปลายทาง")
        else:
            pdf_data = {
                "date": (datetime.now() + timedelta(hours=7)).strftime('%d/%m/%Y'),
                "items": clean_items,
                "to_loc": to_location,
                "transfer_type": transfer_type,
                "s_old": s_old if s_old else "............................",
                "s_new": s_new if s_new else "............................",
                "it_staff": it_staff if it_staff else "............................"
            }
            try:
                pdf_out = create_transfer_pdf(pdf_data)
                st.download_button(label="📥 ดาวน์โหลดไฟล์ PDF", data=bytes(pdf_out), file_name="Transfer_Form.pdf", mime="application/pdf")
                st.success("✅ ครบถ้วนทุกส่วนแล้วครับ!")
            except Exception as e:
                st.error(f"Error: {e}")
