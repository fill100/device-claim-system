import streamlit as st
# โค้ดสำหรับซ่อนเมนูอัตโนมัติของ Streamlit
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* ซ่อนเมนูเดิมที่ชื่อ app/Wesgan */
    [data-testid="stSidebarNavItems"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# จากนั้นค่อยเขียน Sidebar ในแบบที่เราต้องการ
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. จัดการรายชื่อ Worksheet (Session State) ---
INITIAL_SHEETS = [
    "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = INITIAL_SHEETS.copy()

EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์"
    , "สถานะ"
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

# ฟังก์ชันสำหรับ Export CSV
def convert_df(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8-sig')

# --- 2. Sidebar: ตั้งค่าและ Export ---
st.sidebar.title("🛠️ ตั้งค่าและรายงาน")

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

# ส่วนเพิ่ม/ลบ Worksheet
with st.sidebar.expander("🆕 เพิ่มอุปกรณ์ใหม่"):
    new_device = st.text_input("ระบุชื่ออุปกรณ์ใหม่:")
    if st.button("➕ สร้างหน้าใหม่"):
        if new_device and new_device not in st.session_state.available_sheets:
            try:
                new_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                conn.create(worksheet=new_device, data=new_df)
                st.session_state.available_sheets.append(new_device)
                st.rerun()
            except: st.error("สร้างไม่สำเร็จ")

st.sidebar.markdown("---")
selected_sheet = st.sidebar.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)

with st.sidebar.expander("⚠️ ลบอุปกรณ์นี้"):
    confirm_delete = st.checkbox(f"ยืนยันลบ '{selected_sheet}'")
    if st.button("🗑️ ยืนยันการลบ"):
        if confirm_delete and len(st.session_state.available_sheets) > 1:
            st.session_state.available_sheets.remove(selected_sheet)
            st.rerun()

# --- 3. ดึงข้อมูล ---
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

# เพิ่มปุ่มดาวน์โหลดใน Sidebar หลังดึงข้อมูลสำเร็จ
# ส่วน Export Report (นำกลับมาแล้วครับ)
st.sidebar.subheader("📊 Export Report")
if not df.empty:
    st.sidebar.download_button(f"📥 Download {selected_sheet} (CSV)", convert_df(df), f"{selected_sheet}.csv", "text/csv")

if st.sidebar.button("📦 Prepare All Devices Report"):
    full_report = handle_export_all()
    if full_report is not None:
        st.sidebar.download_button("✅ Click to Download All", convert_df(full_report), "all_devices.csv", "text/csv")

# --- 4. Dashboard ---
st.title(f"📑 Claim System: {selected_sheet}")
status_col = df["สถานะ"].str.strip().str.lower()
inprogress = len(df[status_col == "inprogress"])
done = len(df[status_col == "done"])

c1, c2, c3 = st.columns(3)
c1.metric("ทั้งหมด", len(df))
c2.markdown(f'<div style="background-color:#FFD700; padding:10px; border-radius:10px; text-align:center; color:black;"><b>In Progress:</b> {inprogress}</div>', unsafe_allow_html=True)
c3.markdown(f'<div style="background-color:#28a745; padding:10px; border-radius:10px; text-align:center; color:white;"><b>Done:</b> {done}</div>', unsafe_allow_html=True)

from datetime import datetime, timedelta
# --- 5. เพิ่มรายการใหม่ (จัดระเบียบย่อหน้าใหม่ทั้งหมด) ---
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
            
        # บรรทัดนี้ต้องอยู่ตรงกับ f1, f2 (ภายใต้ with st.form)
        submit_btn = st.form_submit_button("บันทึกข้อมูล")

        if submit_btn:
            if sn_f:
                # ปรับเวลาไทย UTC+7
                now_thailand = datetime.now() + timedelta(hours=7)
                time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
                
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": time_str, 
                    "วันทีนำไปติดตั้งใหม่": dt_clm.strftime("%Y-%m-%d") if dt_clm else "", 
                    "สาขา": br, 
                    "counter": cnt, 
                    "Serial เครื่องที่เสีย": sn_f, 
                    "สถานะ": stt, 
                    "Serial เครื่องที่เปลี่ยนใหม่": sn_n
                }])
                
                # รวมข้อมูลและอัปเดตไปยัง Google Sheets
                try:
                    df = pd.concat([df, new_row], ignore_index=True).astype(str)
                    conn.update(worksheet=selected_sheet, data=df)
                    
                    st.success(f"บันทึกข้อมูลสำเร็จเมื่อเวลา {time_str}")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
            else:
                st.error("กรุณาระบุ Serial เครื่องที่เสีย")
# --- 6. แก้ไขและลบแถว (ปรับปรุงให้แก้ไขได้ครบทุกคอลัมน์) ---
if not df.empty:
    with st.expander("📝 แก้ไข หรือ ลบรายการ"):
        # เลือกรายการที่จะจัดการจาก Serial เครื่องที่เสีย
        sn_list = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการจัดการ:", sn_list)
        
        # ดึง Index และข้อมูลแถวนั้นมา
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        row = df.loc[idx]

        with st.form("edit_full_form"):
            st.markdown(f"### กำลังแก้ไขข้อมูลของ Serial: {sel_sn}")
            e1, e2, e3 = st.columns(3)
            
            with e1:
                # 1. วันที่รับแจ้ง
                new_d_rec = st.text_input("วันที่รับแจ้ง", value=str(row["วันที่รับแจ้ง"]))
                # 3. วันทีนำไปติดตั้งใหม่
                try: curr_d_ins = datetime.strptime(str(row["วันทีนำไปติดตั้งใหม่"]), "%Y-%m-%d")
                except: curr_d_ins = None
                new_d_ins = st.date_input("วันทีนำไปติดตั้งใหม่", value=curr_d_ins)
                # 4. สาขา
                new_b = st.selectbox("สาขา", BRANCH_LIST, index=BRANCH_LIST.index(str(row["สาขา"])) if str(row["สาขา"]) in BRANCH_LIST else 0)
                # 5. Counter
                new_c = st.text_input("Counter", value=str(row["counter"]))
                # 6. Serial เครื่องที่เสีย (หากแก้ตัวนี้ ระบบจะอัปเดตค่าใหม่ลงไป)
                new_sn_f = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))

            with e2:
                # 7. Serial เครื่องที่ส่งให้ศูนย์
                new_sn_ctr = st.text_input("Serial เครื่องที่ส่งให้ศูนย์", value=str(row["Serial เครื่องที่ส่งให้ศูนย์"]))
                # 9. สถานะ
                new_s = st.selectbox("สถานะ", ["inprogress", "Done"], index=0 if str(row["สถานะ"]).lower() == "inprogress" else 1)
            
            st.divider()
            b1, b2 = st.columns(2)
            
            if b1.form_submit_button("💾 บันทึกการแก้ไขทั้งหมด"):
                # อัปเดตค่าลงใน DataFrame ตัวหลัก (บังคับเป็น object เพื่อไม่ให้ติดเรื่อง Dtype)
                df = df.astype(object)
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec
                df.at[idx, "วันที่ส่งเคลม"] = new_d_clm.strftime("%Y-%m-%d") if new_d_clm else ""
                df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                df.at[idx, "Serial เครื่องที่เปลี่ยนใหม่"] = new_sn_new
                df.at[idx, "สถานะ"] = new_s
                
                # ส่งข้อมูลกลับไปที่ Google Sheets
                conn.update(worksheet=selected_sheet, data=df.astype(str))
                st.success("✅ อัปเดตข้อมูลทั้ง 9 คอลัมน์เรียบร้อยแล้ว!")
                st.rerun()
                
            if b2.form_submit_button("🗑️ ลบรายการนี้ออก"):
                df_dropped = df.drop(idx)
                conn.update(worksheet=selected_sheet, data=df_dropped.astype(str))
                st.warning(f"ลบรายการ {sel_sn} ออกแล้ว")
                st.rerun()
# --- 7. ตารางค้นหา ---
st.divider()
st.subheader("🔍 ค้นหาข้อมูล")
q = st.text_input("ค้นหา:", placeholder="Serial, สาขา...", label_visibility="collapsed")
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]
st.dataframe(view, use_container_width=True, hide_index=True)
