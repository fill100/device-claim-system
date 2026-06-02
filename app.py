import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, date

# --- ตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="💻 JVFS IT Management System", layout="wide")

# --- ปรับปรุงสีตัวหนังสือให้ชัดเจนที่สุด (High Contrast) ---
st.markdown("""
    <style>
    /* บังคับสีตัวหนังสือในหน้าหลักทั้งหมดให้เข้มขึ้น */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #ffffff; 
    }
    
    /* ซ่อนเมนูเดิม */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
    
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
    
    # ป้องกันบั๊ก KeyError ด้วยการใช้กลไกหาหน้าหลักที่ปลอดภัยของเซิร์ฟเวอร์
    try:
        from streamlit.runtime.pages_manager import get_pages_manager
        pages_manager = get_pages_manager()
        main_page_key = next(iter(pages_manager.get_pages().keys()))
        main_page_info = pages_manager.get_pages()[main_page_key]
        st.page_link(main_page_info["script_path"], label="Device Claim", icon="📑")
    except Exception:
        # แผนสำรองกรณีหน้าหลักถูกเปลี่ยนชื่อใน Github
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
                    # แก้ไขบั๊กจุดนี้: เปลี่ยนจาก conn.create เป็น conn.update เพื่อให้รองรับคำสั่งของ gsheets ไลบรารี
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
with st.expander("➕ เพิ่มรายการแจ้งซ่อม (กรอกพร้อมกันได้หลายรายการ)"):
    if "editor_version" not in st.session_state:
        st.session_state.editor_version = 0

    default_buffer = pd.DataFrame([{
        "สาขา": "One Bangkok", "counter": "", "Serial เครื่องที่เสีย (บังคับ)": "", "Serial เครื่องที่ส่งให้ศูนย์": "", "สถานะ": "inprogress"
    }])

    st.markdown("💡 *คุณสามารถกด `+ Add row` ที่ท้ายตารางเพื่อพิมพ์เพิ่ม หรือก๊อปปี้ข้อมูลจาก Excel มาวาง (Ctrl+V) ได้เลย*")
    
    edited_input = st.data_editor(
        default_buffer,
        num_rows="dynamic",
        column_config={
            "สาขา": st.column_config.SelectboxColumn("สาขา", options=BRANCH_LIST, required=True),
            "counter": st.column_config.TextColumn("Counter"),
            "Serial เครื่องที่เสีย (บังคับ)": st.column_config.TextColumn("Serial เครื่องที่เสีย", required=True),
            "Serial เครื่องที่ส่งให้ศูนย์": st.column_config.TextColumn("Serial เครื่องที่ส่งให้ศูนย์"),
            "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["inprogress", "Done"], required=True),
        },
        use_container_width=True,
        key=f"bulk_editor_{st.session_state.editor_version}"
    )

    if st.button("💾 บันทึกทุกรายการลงฐานข้อมูล", type="primary"):
        valid_rows = edited_input[edited_input["Serial เครื่องที่เสีย (บังคับ)"].fillna("").str.strip() != ""].copy()
        
        if not valid_rows.empty:
            now_thailand = datetime.now() + timedelta(hours=7)
            time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
            
            new_rows_list = []
            for _, row in valid_rows.iterrows():
                sn_center = "" if str(row["Serial เครื่องที่ส่งให้ศูนย์"]).strip().lower() == "none" else row["Serial เครื่องที่ส่งให้ศูนย์"]
                
                new_rows_list.append({
                    "วันที่รับแจ้ง": time_str,
                    "วันทีนำไปติดตั้งใหม่": "",
                    "สาขา": row["สาขา"],
                    "counter": row["counter"],
                    "Serial เครื่องที่เสีย": row["Serial เครื่องที่เสีย (บังคับ)"],
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_center,
                    "สถานะ": row["สถานะ"]
                })
            
            new_df_to_add = pd.DataFrame(new_rows_list)
            df = pd.concat([df, new_df_to_add], ignore_index=True).astype(str)
            
            save_df = df.copy()
            if has_trackmo_col and "สถานะ" in save_df.columns:
                save_df = save_df.rename(columns={"สถานะ": "แก้ในTrackMo"})

            try:
                conn.update(worksheet=selected_sheet, data=save_df)
                st.success(f"🎉 บันทึกข้อมูลเรียบร้อยแล้วทั้งหมด {len(new_rows_list)} รายการ!")
                st.session_state.editor_version += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ ไม่สามารถบันทึกได้เนื่องจากข้อผิดพลาด: {e}")
        else:
            st.warning("⚠️ โปรดกรอกข้อมูลในช่อง 'Serial เครื่องที่เสีย' อย่างน้อย 1 รายการก่อนกดบันทึก")

# --- 7. ส่วนแก้ไข หรือ ลบรายการ ---
if not df.empty:
    with st.expander("📝 แก้ไข หรือ ลบรายการ"):
        sn_list = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial ที่ต้องการจัดการ:", sn_list)
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        row = df.loc[idx]
        
        val_d_rec = "" if str(row["วันที่รับแจ้ง"]).lower() == "nan" else str(row["วันที่รับแจ้ง"])
        val_counter = "" if str(row["counter"]).lower() == "nan" else str(row["counter"])
        val_sn_ctr = "" if str(row["Serial เครื่องที่ส่งให้ศูนย์"]).lower() == "nan" else str(row["Serial เครื่องที่ส่งให้ศูนย์"])

        # แก้ไขจุดเสี่ยงล่ม: ประมวลผลวันที่อย่างปลอดภัยและป้องกัน Exception ค่าว่าง
        try:
            date_str = str(row["วันทีนำไปติดตั้งใหม่"]).strip()
            if date_str and date_str.lower() != "nan" and date_str != "":
                curr_d_ins = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                curr_d_ins = date.today()
        except Exception:
            curr_d_ins = date.today()

        with st.form("edit_full_form"):
            e1, e2, e3 = st.columns(3)
            with e1:
                new_d_rec = st.text_input("วันที่รับแจ้ง", value=val_d_rec)
                new_d_ins = st.date_input("วันทีนำไปติดตั้งใหม่", value=curr_d_ins)
                new_s = st.selectbox("สถานะ", ["inprogress", "Done"], index=0 if str(row["สถานะ"]).lower() == "inprogress" else 1)
            with e2:
                new_b = st.selectbox("สาขา", BRANCH_LIST, index=BRANCH_LIST.index(str(row["สาขา"])) if str(row["สาขา"]) in BRANCH_LIST else 0)
                new_c = st.text_input("Counter", value=val_counter)
            with e3:
                new_sn_f = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))
                new_sn_ctr = st.text_input("Serial เครื่องที่ส่งให้ศูนย์", value=val_sn_ctr)
            
            submit_edit = st.form_submit_button("💾 บันทึกการแก้ไข")
            
            if submit_edit:
                df = df.astype(object)
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec
                df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                df.at[idx, "สถานะ"] = new_s
                
                save_df = df.copy()
                if has_trackmo_col and "สถานะ" in save_df.columns:
                    save_df = save_df.rename(columns={"สถานะ": "แก้ในTrackMo"})
                
                try:
                    conn.update(worksheet=selected_sheet, data=save_df.astype(str))
                    st.success("อัปเดตเรียบร้อย!")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการอัปเดต: {e}")
        
        st.markdown("---")
        st.markdown("🛑 **โซนลบข้อมูลออกจากระบบ**")
        confirm_row_delete = st.checkbox(f"ฉันตรวจสอบดีแล้วและยืนยันว่าต้องการลบข้อมูล Serial: `{sel_sn}` นี้")
        
        if st.button("🗑️ ยืนยันการลบรายการนี้", type="primary"):
            if confirm_row_delete:
                df = df.drop(idx)
                save_df = df.copy()
                if has_trackmo_col and "สถานะ" in save_df.columns:
                    save_df = save_df.rename(columns={"สถานะ": "แก้ในTrackMo"})
                try:
                    conn.update(worksheet=selected_sheet, data=save_df.astype(str))
                    st.success("🎉 ลบข้อมูลรายการดังกล่าวออกจากฐานข้อมูลสำเร็จ!")
                    st.rerun()
                except Exception as e:
                    st.error(f"ไม่สามารถลบข้อมูลได้เนื่องจาก: {e}")
            else:
                st.warning("⚠️ โปรดคลิกเลือกที่ช่อง 'ฉันตรวจสอบดีแล้วและยืนยัน...' ก่อนกดปุ่มลบ")

# --- 8. ตารางผลลัพธ์ ---
st.divider()
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]

st.dataframe(view, use_container_width=True, hide_index=True)
