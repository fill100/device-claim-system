import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import importlib

# --- 1. ตั้งค่าหน้ากระดาษ (ทำครั้งเดียวที่บนสุดของไฟล์หลัก) ---
st.set_page_config(page_title="💻 IT Management System", layout="wide")

# จัดการ State สำหรับควบคุมการสลับหน้า
if "current_page" not in st.session_state:
    st.session_state.current_page = "Device Claim"

# --- 2. ปรับปรุงสไตล์ CSS (คงไว้ตามดีไซน์เดิมของคุณ) ---
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

# --- 3. เมนูนำทาง Sidebar แบบ Single-page ยุบรวมเหลือชุดเดียว ---
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

# --- 4. การจัดการแบ่งหน้าตาม State ---

# ----------------- หน้าที่ 1: DEVICE CLAIM -----------------
if st.session_state.current_page == "Device Claim":
    
    # เชื่อมต่อฐานข้อมูล
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
        st.stop()

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

    # ตั้งค่าและรายงานใน Sidebar
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

    # --- หน้าหลัก Device Claim ---
    st.title("📑 Claim Management System")

    col_ws, col_search = st.columns([1, 2])
    with col_ws:
        selected_sheet = st.selectbox("📂 เลือก Worksheet:", st.session_state.available_sheets)

    # ดึงข้อมูลจาก Google Sheets
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

    # --- Dashboard Metrics ---
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

    # --- 🌟 ฟังก์ชัน: เพิ่มรายการแจ้งซ่อมแบบหลายรายการ (Bulk Import) ---
    with st.expander("➕ เพิ่มรายการแจ้งซ่อม (เพิ่มได้ทีละหลายรายการ)"):
        st.write("💡 พี่สามารถก๊อปปี้ข้อมูลจาก Excel/Sheets มาวาง หรือพิมพ์เพิ่มแถวในตารางด้านล่างได้เลยครับ")
        
        # คีย์ข้อมูลจำลองตั้งต้น
        if "bulk_add_df" not in st.session_state:
            st.session_state.bulk_add_df = pd.DataFrame([{
                "สาขา": BRANCH_LIST[0], "counter": "", "Serial เครื่องที่เสีย": "", 
                "Serial เครื่องที่ส่งให้ศูนย์": "", "สถานะ": "inprogress", "วันทีนำไปติดตั้งใหม่": None
            }])
            
        edited_add_df = st.data_editor(
            st.session_state.bulk_add_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "สาขา": st.column_config.SelectboxColumn("สาขา", options=BRANCH_LIST, required=True),
                "counter": st.column_config.TextColumn("Counter"),
                "Serial เครื่องที่เสีย": st.column_config.TextColumn("Serial เครื่องที่เสีย (บังคับ)", required=True),
                "Serial เครื่องที่ส่งให้ศูนย์": st.column_config.TextColumn("Serial เครื่องที่ส่งให้ศูนย์"),
                "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["inprogress", "Done"], required=True),
                "วันทีนำไปติดตั้งใหม่": st.column_config.DateColumn("วันทีนำไปติดตั้งใหม่")
            },
            key="bulk_add_editor"
        )
        
        if st.button("💾 บันทึกรายการทั้งหมดที่เพิ่ม", type="primary"):
            # กรองแถวที่กรอก Serial เครื่องเสียจริงๆ ไม่เป็นค่าว่าง
            valid_rows = edited_add_df[edited_add_df["Serial เครื่องที่เสีย"].str.strip() != ""].copy()
            
            if valid_rows.empty:
                st.error("⚠️ ไม่พบข้อมูลที่กรอกเลข Serial เครื่องที่เสีย")
            else:
                now_thailand = datetime.now() + timedelta(hours=7)
                time_str = now_thailand.strftime("%Y-%m-%d %H:%M")
                
                prepared_rows = []
                for _, row in valid_rows.iterrows():
                    dt_val = row["วันทีนำไปติดตั้งใหม่"]
                    prepared_rows.append({
                        "วันที่รับแจ้ง": time_str,
                        "วันทีนำไปติดตั้งใหม่": dt_val.strftime("%Y-%m-%d") if pd.notnull(dt_val) else "",
                        "สาขา": row["สาขา"],
                        "counter": row["counter"],
                        "Serial เครื่องที่เสีย": row["Serial เครื่องที่เสีย"],
                        "Serial เครื่องที่ส่งให้ศูนย์": row["Serial เครื่องที่ส่งให้ศูนย์"],
                        "สถานะ": row["สถานะ"]
                    })
                
                new_data_df = pd.DataFrame(prepared_rows).astype(str)
                df = pd.concat([df, new_data_df], ignore_index=True).astype(str)
                
                try:
                    conn.update(worksheet=selected_sheet, data=df)
                    st.success(f"บันทึกข้อมูลสำเร็จทั้งหมด {len(new_data_df)} รายการ!")
                    if "bulk_add_df" in st.session_state:
                        del st.session_state.bulk_add_df # รีเซ็ตตาราง
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")

    # --- 🌟 ฟังก์ชัน: แก้ไข หรือ ลบรายการทีละหลายรายการ (Bulk Edit / Delete) ---
    if not df.empty:
        with st.expander("📝 แก้ไข หรือ ลบรายการ (เลือกทำพร้อมกันได้หลายรายการ)"):
            st.write("💡 ติ๊กถูกที่ช่อง **'เลือกเพื่อลบ'** หน้ารายการเพื่อเลือกข้อมูลที่ต้องการลบพร้อมกัน หรือแก้ในตารางแล้วกดบันทึก")
            
            # ยัด Checkbox นำหน้าข้อมูลในตารางแก้ไข
            edit_df = df.copy()
            edit_df.insert(0, "เลือกเพื่อลบ", False)
            
            edited_table = st.data_editor(
                edit_df,
                use_container_width=True,
                column_config={
                    "เลือกเพื่อลบ": st.column_config.CheckboxColumn("เลือกเพื่อลบ", default=False),
                    "วันที่รับแจ้ง": st.column_config.TextColumn("วันที่รับแจ้ง", disabled=True),
                    "สาขา": st.column_config.SelectboxColumn("สาขา", options=BRANCH_LIST),
                    "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["inprogress", "Done"])
                },
                key="bulk_edit_delete_editor",
                hide_index=True
            )
            
            del_col, save_col, _ = st.columns([1, 1, 3])
            
            with del_col:
                if st.button("🗑️ ลบรายการที่เลือก", type="secondary", use_container_width=True):
                    # กรองเอาแถวที่ไม่ได้โดนติ๊กเลือกไว้ (ตัวที่โดนติ๊กจะถูกคัดทิ้งไป)
                    items_to_keep = edited_table[edited_table["เลือกเพื่อลบ"] == False].drop(columns=["เลือกเพื่อลบ"])
                    deleted_count = len(df) - len(items_to_keep)
                    
                    if deleted_count == 0:
                        st.warning("⚠️ กรุณาติ๊กถูกเลือกรายการในตารางก่อนกดลบครับ")
                    else:
                        try:
                            conn.update(worksheet=selected_sheet, data=items_to_keep.astype(str))
                            st.success(f"🗑️ ลบรายการสำเร็จทั้งหมด {deleted_count} รายการเรียบร้อย!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"ไม่สามารถลบข้อมูลได้: {e}")
                            
            with save_col:
                if st.button("💾 บันทึกการแก้ไขตาราง", type="primary", use_container_width=True):
                    # ดึงคอลัมน์ checkbox ออกก่อนเซฟคืน Google Sheets
                    final_to_save = edited_table.drop(columns=["เลือกเพื่อลบ"])
                    try:
                        conn.update(worksheet=selected_sheet, data=final_to_save.astype(str))
                        st.success("💾 อัปเดตข้อมูลในตารางเรียบร้อย!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")

    # --- ตารางผลลัพธ์การค้นหาด้านล่างสุด ---
    st.divider()
    view = df.copy()
    if q:
        mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
        view = view[mask]

    st.dataframe(view, use_container_width=True, hide_index=True)

# ----------------- หน้าที่ 2: ASSET SYSTEM -----------------
elif st.session_state.current_page == "Asset System":
    import Wesgan
    if hasattr(Wesgan, 'run_asset_page'):
        Wesgan.run_asset_page()
    else:
        importlib.reload(Wesgan)

# ----------------- หน้าที่ 3: โอนย้ายของ -----------------
elif st.session_state.current_page == "Transfer":
    import Transfer
    if hasattr(Transfer, 'run_transfer_page'):
        Transfer.run_transfer_page()
    else:
        importlib.reload(Transfer)
