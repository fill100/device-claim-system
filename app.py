import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

AVAILABLE_SHEETS = [
    "Signature pad", "Passpost", "Iris Scaner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

selected_sheet = st.sidebar.selectbox("เลือก Worksheet:", AVAILABLE_SHEETS)

# คอลัมน์มาตรฐานตามที่ต้องการ
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "สถานะ"
]

try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        
        # เปลี่ยนชื่อคอลัมน์เก่าเป็น 'สถานะ' เพื่อป้องกัน Error
        if "แก้ในTrackMo" in df.columns:
            df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
            
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[EXPECTED_COLUMNS]
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

st.title(f"📑 JVFS Device Claim System ({selected_sheet})")

# --- ส่วนที่ 1: Dashboard (In Progress=เหลือง, Done=เขียว) ---
st.subheader("📊 ภาพรวมการเคลม")
status_col = df["สถานะ"].astype(str).fillna("").str.strip().str.lower()

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

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูลใหม่ ---
with st.expander("➕ เพิ่มรายการใหม่"):
    with st.form("main_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            branch = st.selectbox("สาขา", ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา", "มุกดาหาร", "ชลบุรี"])
            counter = st.text_input("Counter")
            sn_fault = st.text_input("S/N เครื่องเสีย (บังคับ)")
        with f2:
            status_val = st.selectbox("สถานะ", ["inprogress", "Done"])
            date_c = st.date_input("วันที่ส่งเคลม", value=None)
            sn_new = st.text_input("S/N เครื่องใหม่")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not sn_fault:
                st.warning("⚠️ กรุณากรอก S/N เครื่องที่เสีย")
            else:
                new_data = pd.DataFrame([{
                    "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "วันที่ส่งเคลม": date_c.strftime("%Y-%m-%d") if date_c else "",
                    "สาขา": branch, "counter": counter, "Serial เครื่องที่เสีย": sn_fault,
                    "สถานะ": status_val, "Serial เครื่องที่เปลี่ยนใหม่": sn_new
                }])
                updated_df = pd.concat([df, new_data], ignore_index=True)[EXPECTED_COLUMNS]
                conn.update(worksheet=selected_sheet, data=updated_df)
                st.success("✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ตารางแสดงข้อมูล ---
st.subheader("🔍 ค้นหาข้อมูล")
q = st.text_input("ค้นหา:", placeholder="Serial, สาขา...", label_visibility="collapsed")
view = df.copy()
if q:
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]
st.dataframe(view, use_container_width=True, hide_index=True)

# --- ส่วนที่ 4: อัปเดตสถานะ/ข้อมูล (แก้ไขได้ทุกฟิลด์) ---
if not view.empty:
    with st.expander("📝 อัปเดตสถานะ/ข้อมูล"):
        sn_list = view["Serial เครื่องที่เสีย"].astype(str).unique().tolist()
        sel_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการแก้ไข:", sn_list)
        
        row = df[df["Serial เครื่องที่เสีย"].astype(str) == sel_sn].iloc[0]
        target_idx = df.index[df["Serial เครื่องที่เสีย"].astype(str) == sel_sn].tolist()[0]
        
        with st.form("edit_form_final"):
            col_a, col_b = st.columns(2)
            with col_a:
                # วันที่รับแจ้ง
                try: val_rec = datetime.strptime(str(row["วันที่รับแจ้ง"]), "%Y-%m-%d %H:%M")
                except: val_rec = datetime.now()
                new_date_rec = st.date_input("วันที่รับแจ้ง", value=val_rec)
                
                # วันที่ส่งเคลม
                try: val_claim = datetime.strptime(str(row["วันที่ส่งเคลม"]), "%Y-%m-%d")
                except: val_claim = None
                new_date_claim = st.date_input("วันที่ส่งเคลม", value=val_claim)
                
                # วันทีนำไปติดตั้งใหม่
                try: val_inst = datetime.strptime(str(row["วันทีนำไปติดตั้งใหม่"]), "%Y-%m-%d")
                except: val_inst = None
                new_date_inst = st.date_input("วันทีนำไปติดตั้งใหม่", value=val_inst)

                branches = ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา", "มุกดาหาร", "ชลบุรี"]
                curr_b = str(row["สาขา"]).strip()
                new_branch = st.selectbox("สาขา", branches, index=branches.index(curr_b) if curr_b in branches else 0)

            with col_b:
                new_counter = st.text_input("counter", value=str(row["counter"]))
                new_sn_faulty = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))
                new_sn_center = st.text_input("Serial เครื่องที่ส่งให้ศูนย์ทดแทนของเดิม", value=str(row["Serial เครื่องที่ส่งให้ศูนย์"]))
                
                st_opts = ["inprogress", "Done"]
                curr_s = str(row["สถานะ"]).strip().lower()
                new_status = st.selectbox("สถานะ", ["inprogress", "Done"], index=st_opts.index(curr_s) if curr_s in st_opts else 0)

            if st.form_submit_button("💾 ยืนยันการอัปเดต"):
                df.at[target_idx, "วันที่รับแจ้ง"] = new_date_rec.strftime("%Y-%m-%d %H:%M")
                df.at[target_idx, "วันที่ส่งเคลม"] = new_date_claim.strftime("%Y-%m-%d") if new_date_claim else ""
                df.at[target_idx, "วันทีนำไปติดตั้งใหม่"] = new_date_inst.strftime("%Y-%m-%d") if new_date_inst else ""
                df.at[target_idx, "สาขา"] = new_branch
                df.at[target_idx, "counter"] = new_counter
                df.at[target_idx, "Serial เครื่องที่เสีย"] = new_sn_faulty
                df.at[target_idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_center
                df.at[target_idx, "สถานะ"] = new_status
                
                conn.update(worksheet=selected_sheet, data=df)
                st.success("✅ อัปเดตข้อมูลเรียบร้อย!")
                st.rerun()
