import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

AVAILABLE_SHEETS = [
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

# --- 1. Sidebar & Export ---
st.sidebar.markdown("### 📁 เมนูจัดการข้อมูล")
selected_sheet = st.sidebar.selectbox("เลือก Worksheet:", AVAILABLE_SHEETS)

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

# --- 5. แก้ไขข้อมูล ---
if not df.empty:
    with st.expander("📝 อัปเดตสถานะ/ข้อมูล"):
        sn_list = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการแก้ไข:", sn_list)
        row = df[df["Serial เครื่องที่เสีย"] == sel_sn].iloc[0]
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        
        with st.form("edit_form_final"):
            e1, e2 = st.columns(2)
            with e1:
                try: d_rec = datetime.strptime(str(row["วันที่รับแจ้ง"]), "%Y-%m-%d %H:%M")
                except: d_rec = datetime.now()
                new_d_rec = st.date_input("วันที่รับแจ้ง", value=d_rec)
                
                try: d_clm = datetime.strptime(str(row["วันที่ส่งเคลม"]), "%Y-%m-%d")
                except: d_clm = None
                new_d_clm = st.date_input("วันที่ส่งเคลม", value=d_clm)
                
                try: d_ins = datetime.strptime(str(row["วันทีนำไปติดตั้งใหม่"]), "%Y-%m-%d")
                except: d_ins = None
                new_d_ins = st.date_input("วันทีนำไปติดตั้งใหม่", value=d_ins)
                
                # แก้ไขสาขาในโหมด Edit
                curr_b = str(row["สาขา"]).strip()
                new_b = st.selectbox("สาขา", BRANCH_LIST, index=BRANCH_LIST.index(curr_b) if curr_b in BRANCH_LIST else 0)
            with e2:
                new_c = st.text_input("counter", value=str(row["counter"]))
                new_sn_f = st.text_input("Serial เครื่องที่เสีย", value=str(row["Serial เครื่องที่เสีย"]))
                new_sn_ctr = st.text_input("Serial เครื่องที่ส่งให้ศูนย์ทดแทนของเดิม", value=str(row["Serial เครื่องที่ส่งให้ศูนย์"]))
                opts = ["inprogress", "Done"]
                curr_s = str(row["สถานะ"]).strip().lower()
                new_s = st.selectbox("สถานะ", ["inprogress", "Done"], index=opts.index(curr_s) if curr_s in opts else 0)
            
            if st.form_submit_button("💾 ยืนยันการอัปเดต"):
                df = df.astype(object)
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec.strftime("%Y-%m-%d %H:%M")
                df.at[idx, "วันที่ส่งเคลม"] = new_d_clm.strftime("%Y-%m-%d") if new_d_clm else ""
                df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                df.at[idx, "สถานะ"] = new_s
                conn.update(worksheet=selected_sheet, data=df.astype(str))
                st.success("อัปเดตเรียบร้อย!")
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
