import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. จัดการรายชื่อ Worksheet (ใช้ Session State เพื่อให้จำค่าที่เพิ่มใหม่ได้)
if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = [
        "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
        "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
        "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
    ]
# รายชื่อสาขาที่อัปเดตใหม่ทั้งหมด
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
# --- ส่วนที่ 1: การจัดการรายชื่อ Worksheet และการเพิ่มหน้าใหม่ ---
if 'available_sheets' not in st.session_state:
    st.session_state.available_sheets = AVAILABLE_SHEETS.copy()

st.sidebar.markdown("### 🆕 เพิ่มอุปกรณ์ใหม่")
new_device = st.sidebar.text_input("ระบุชื่ออุปกรณ์ใหม่:", placeholder="เช่น Scanner, Hub...")

if st.sidebar.button("➕ สร้าง Worksheet ใน Google Sheets"):
    if new_device:
        if new_device not in st.session_state.available_sheets:
            try:
                # สร้าง DataFrame เปล่าที่มีเฉพาะ Header เพื่อใช้สร้าง Sheet ใหม่
                #
                new_sheet_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                
                # ส่งคำสั่งสร้าง Worksheet ใหม่พร้อมข้อมูล Header
                conn.create(worksheet=new_device, data=new_sheet_df)
                
                # เพิ่มชื่อเข้าในรายการของหน้าเว็บ
                st.session_state.available_sheets.append(new_device)
                st.sidebar.success(f"✅ สร้างหน้า '{new_device}' สำเร็จ!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ ไม่สามารถสร้างได้: {e}")
        else:
            st.sidebar.warning("⚠️ ชื่ออุปกรณ์นี้มีอยู่ในระบบแล้ว")
    else:
        st.sidebar.warning("⚠️ กรุณากรอกชื่ออุปกรณ์")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 เมนูจัดการข้อมูล")
# เปลี่ยนมาใช้รายการจาก session_state
selected_sheet = st.sidebar.selectbox("เลือก Worksheet:", st.session_state.available_sheets)

def convert_df(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8-sig')

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Export Report")

EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "สถานะ"
]

# --- 2. ดึงข้อมูล ---
try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        if "แก้ในTrackMo" in df.columns:
            df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
        df = df.astype(str)
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[EXPECTED_COLUMNS]
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# Export Buttons
if not df.empty:
    st.sidebar.download_button(label=f"📥 Download {selected_sheet} (CSV)", data=convert_df(df), file_name=f"report_{selected_sheet}.csv", mime="text/csv")

if st.sidebar.button("📦 Prepare All Devices Report"):
    with st.spinner("กำลังรวบรวม..."):
        all_data = []
        for sheet in AVAILABLE_SHEETS:
            try:
                temp_df = conn.read(worksheet=sheet, ttl="0")
                if temp_df is not None and not temp_df.empty:
                    temp_df["ประเภทอุปกรณ์"] = sheet
                    all_data.append(temp_df)
            except: continue
        if all_data:
            full_df = pd.concat(all_data, ignore_index=True)
            st.sidebar.download_button(label="✅ Click to Download All", data=convert_df(full_df), file_name="all_devices_report.csv", mime="text/csv")

# --- 3. Dashboard ---
st.title(f"📑 JVFS Device Claim System ({selected_sheet})")
status_col = df["สถานะ"].str.strip().str.lower()
total = len(df)
inprogress = len(df[status_col == "inprogress"])
done = len(df[status_col == "done"])

c1, c2, c3 = st.columns(3)
c1.metric("รายการทั้งหมด", total)
with c2:
    st.markdown(f'<div style="background-color:#FFD700; padding:15px; border-radius:10px; text-align:center; color:black;"><small>In Progress</small><br><span style="font-size:24px; font-weight:bold;">{inprogress}</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="background-color:#28a745; padding:15px; border-radius:10px; text-align:center; color:white;"><small>Done</small><br><span style="font-size:24px; font-weight:bold;">{done}</span></div>', unsafe_allow_html=True)
st.divider()

# --- 4. ฟอร์มเพิ่มข้อมูลใหม่ ---
with st.expander("➕ เพิ่มรายการใหม่"):
    with st.form("main_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            branch = st.selectbox("สาขา", BRANCH_LIST) # ใช้รายการสาขาใหม่
            counter = st.text_input("Counter")
            sn_fault = st.text_input("S/N เครื่องเสีย (บังคับ)")
        with f2:
            status_val = st.selectbox("สถานะ", ["inprogress", "Done"])
            date_c = st.date_input("วันที่ส่งเคลม", value=None)
            sn_new = st.text_input("S/N เครื่องใหม่")
        if st.form_submit_button("บันทึกข้อมูล"):
            if not sn_fault: st.warning("กรุณากรอก S/N เครื่องเสีย")
            else:
                new_row = pd.DataFrame([{"วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"), "วันที่ส่งเคลม": date_c.strftime("%Y-%m-%d") if date_c else "", "สาขา": branch, "counter": counter, "Serial เครื่องที่เสีย": sn_fault, "สถานะ": status_val, "Serial เครื่องที่เปลี่ยนใหม่": sn_new}])
                updated = pd.concat([df, new_row], ignore_index=True).astype(str)
                conn.update(worksheet=selected_sheet, data=updated)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 5: แก้ไขและลบข้อมูล (อัปเดตสถานะ/รายละเอียด) ---
if not df.empty:
    with st.expander("📝 อัปเดตสถานะ หรือ ลบข้อมูล"):
        # เลือกรายการที่จะจัดการ
        sn_list = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการจัดการ:", sn_list)
        
        row = df[df["Serial เครื่องที่เสีย"] == sel_sn].iloc[0]
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        
        # แบ่งเป็น 2 คอลัมน์สำหรับปุ่ม อัปเดต และ ปุ่มลบ
        with st.form("edit_delete_form"):
            e1, e2 = st.columns(2)
            with e1:
                # ... (ส่วนอินพุตข้อมูลคงเดิมเหมือนเวอร์ชันล่าสุด) ...
                try: d_rec = datetime.strptime(str(row["วันที่รับแจ้ง"]), "%Y-%m-%d %H:%M")
                except: d_rec = datetime.now()
                new_d_rec = st.date_input("วันที่รับแจ้ง", value=d_rec)
                
                try: d_clm = datetime.strptime(str(row["วันที่ส่งเคลม"]), "%Y-%m-%d")
                except: d_clm = None
                new_d_clm = st.date_input("วันที่ส่งเคลม", value=d_clm)
                
                new_b = st.selectbox("สาขา", BRANCH_LIST, index=BRANCH_LIST.index(str(row["สาขา"])) if str(row["สาขา"]) in BRANCH_LIST else 0)
            
            with e2:
                new_c = st.text_input("counter", value=str(row["counter"]))
                new_sn_f = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))
                new_s = st.selectbox("สถานะ", ["inprogress", "Done"], index=0 if str(row["สถานะ"]).lower() == "inprogress" else 1)

            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            
            # ปุ่มที่ 1: ยืนยันการอัปเดต
            if col_btn1.form_submit_button("💾 ยืนยันการอัปเดต"):
                df = df.astype(object)
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec.strftime("%Y-%m-%d %H:%M")
                df.at[idx, "วันที่ส่งเคลม"] = new_d_clm.strftime("%Y-%m-%d") if new_d_clm else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "สถานะ"] = new_s
                
                conn.update(worksheet=selected_sheet, data=df.astype(str))
                st.success("✅ อัปเดตข้อมูลเรียบร้อย!")
                st.rerun()

            # ปุ่มที่ 2: ลบข้อมูล (สีแดง)
            if col_btn2.form_submit_button("🗑️ ลบรายการนี้ออกจากระบบ"):
                # ลบแถวตาม index ที่เลือก
                df_dropped = df.drop(idx)
                
                # อัปเดตข้อมูลที่ลบแล้วกลับไปยัง Google Sheets
                conn.update(worksheet=selected_sheet, data=df_dropped.astype(str))
                st.warning(f"🔥 ลบรายการ Serial: {sel_sn} เรียบร้อยแล้ว")
                st.rerun()

# --- 6. ตารางค้นหาข้อมูล ---
st.divider()
st.subheader("🔍 ค้นหาข้อมูล")
q = st.text_input("ค้นหา:", placeholder="Serial, สาขา, สถานะ...", label_visibility="collapsed")
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]
st.dataframe(view, use_container_width=True, hide_index=True)
