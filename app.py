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

# --- Sidebar & Export Logic ---
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

try:
    df = conn.read(worksheet=selected_sheet, ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        if "แก้ในTrackMo" in df.columns:
            df = df.rename(columns={"แก้ในTrackMo": "สถานะ"})
        
        # --- จุดแก้ไขสำคัญ: บังคับทุกคอลัมน์เป็น String เพื่อป้องกัน TypeError ---
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

# Export Buttons in Sidebar
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

# --- Dashboard ---
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

# --- ส่วนที่ 4: ฟอร์มเพิ่มข้อมูลใหม่ (ย้ายขึ้นมาเพื่อให้ข้อมูลอัปเดตก่อนแสดงตาราง) ---
with st.expander("➕ เพิ่มรายการใหม่"):
    # ... (โค้ดฟอร์มบันทึกข้อมูลเหมือนเดิม) ...
    # เมื่อบันทึกสำเร็จ ระบบจะใช้ st.rerun() เพื่อโหลดข้อมูลใหม่ทั้งหมด

# --- ส่วนที่ 6: แก้ไขข้อมูล (ย้ายขึ้นมาเพื่อให้ผลการแก้ไขสะท้อนลงตารางด้านล่าง) ---
if not df.empty:
    with st.expander("📝 อัปเดตสถานะ/ข้อมูล"):
        # ใช้ df ตัวหลักในการหา Serial เพื่อความแม่นยำ
        all_sn = df["Serial เครื่องที่เสีย"].unique().tolist()
        sel_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการแก้ไข:", all_sn)
        
        row = df[df["Serial เครื่องที่เสีย"] == sel_sn].iloc[0]
        idx = df.index[df["Serial เครื่องที่เสีย"] == sel_sn].tolist()[0]
        
        with st.form("edit_form_final"):
            # ... (ส่วนอินพุตข้อมูลคงเดิมเหมือนเวอร์ชันล่าสุด) ...
            
            if st.form_submit_button("💾 ยืนยันการอัปเดต"):
                df = df.astype(object)
                # บันทึกค่าใหม่ลงใน df
                df.at[idx, "วันที่รับแจ้ง"] = new_d_rec.strftime("%Y-%m-%d %H:%M")
                df.at[idx, "วันที่ส่งเคลม"] = new_d_clm.strftime("%Y-%m-%d") if new_d_clm else ""
                df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_d_ins.strftime("%Y-%m-%d") if new_d_ins else ""
                df.at[idx, "สาขา"] = new_b
                df.at[idx, "counter"] = new_c
                df.at[idx, "Serial เครื่องที่เสีย"] = new_sn_f
                df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_ctr
                df.at[idx, "สถานะ"] = new_s
                
                # อัปเดตลง Google Sheets และสั่ง rerun ทันทีเพื่อให้ตารางด้านล่างเปลี่ยนตาม
                conn.update(worksheet=selected_sheet, data=df.astype(str))
                st.success("✅ อัปเดตข้อมูลสำเร็จและกำลังรีเฟรชตาราง...")
                st.rerun()

st.divider()

# --- ส่วนที่ 5: ตารางค้นหาข้อมูล (วางไว้ล่างสุดเพื่อให้เห็นข้อมูลที่อัปเดตแล้ว) ---
st.subheader("🔍 ตารางแสดงข้อมูลและผลการค้นหา")
q = st.text_input("พิมพ์เพื่อค้นหา (Serial, สาขา, สถานะ):", placeholder="ตัวอย่าง: Done, One Bangkok...", label_visibility="collapsed")

# สร้างตัวแปร view หลังจากที่อาจมีการกดอัปเดตข้อมูลไปแล้ว
view = df.copy()
if q:
    # ค้นหาครอบคลุมทุกคอลัมน์
    mask = view.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
    view = view[mask]

# แสดงตาราง (ข้อมูลในนี้จะเปลี่ยนตามการแก้ไขด้านบนทันทีเพราะอยู่หลังคำสั่ง rerun)
st.dataframe(
    view, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "สถานะ": st.column_config.TextColumn("สถานะ", help="inprogress หรือ Done")
    }
)
