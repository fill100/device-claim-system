import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# กำหนดชื่อคอลัมน์มาตรฐานตามที่คุณระบุ
EXPECTED_COLUMNS = [
    "วันที่รับแจ้ง", "วันที่ส่งเคลม", "วันทีนำไปติดตั้งใหม่", "สาขา", 
    "counter", "Serial เครื่องที่เสีย", "Serial เครื่องที่ส่งให้ศูนย์", 
    "Serial เครื่องที่เปลี่ยนใหม่", "แก้ในTrackMo"
]

# ดึงข้อมูลหลัก
try:
    df = conn.read(ttl="0")
    
    if df is not None and not df.empty:
        # ล้างช่องว่างหน้า-หลังชื่อคอลัมน์ ป้องกัน KeyError
        df.columns = df.columns.str.strip()
        
        # ตรวจสอบว่าคอลัมน์จาก Sheet มีครบตามที่กำหนดใน EXPECTED_COLUMNS หรือไม่
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ ข้อมูลใน Google Sheets มีคอลัมน์ไม่ครบ ขาดคอลัมน์: {', '.join(missing_cols)}")
            # เพิ่มคอลัมน์ที่ขาดให้เป็นค่าว่างชั่วคราว เพื่อไม่ให้โปรแกรมพัง
            for col in missing_cols:
                df[col] = ""
    else:
        # กรณี Sheet ว่างเปล่า ให้สร้าง DataFrame เปล่าที่มีหัวตารางครบ
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)

except Exception as e:
    st.error(f"❌ ไม่พบการตั้งค่า Spreadsheet หรือไฟล์มีปัญหา: {e}")
    st.stop()

# ข้อมูลสำหรับ Dropdown
branches = ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"]

st.title("📑 JVFS Device Claim System")

# --- ส่วนที่ 1: Dashboard สรุปผล ---
# ปรับตัวนับจำนวนโดยอ้างอิงสถานะจากคอลัมน์ "แก้ในTrackMo" แทนคอลัมน์ "สถานะ" เดิม
if not df.empty and "แก้ในTrackMo" in df.columns:
    st.subheader("📊 ภาพรวมการเคลม")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายการทั้งหมด", len(df))
    # ปรับแต่งการดึงค่าป้องกันเคสที่เป็นค่า NaN หรือไม่ใช่ String
    track_series = df["แก้ในTrackMo"].fillna("").astype(str).str.strip()
    m2.metric("รอดำเนินการ (Pending)", len(df[track_series == "Pending"]))
    m3.metric("กำลังทำ (In Progress)", len(df[track_series == "inprogress"]))
    m4.metric("เสร็จสิ้น (Done)", len(df[track_series == "Done"]))
    st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล ---
with st.expander("➕ เพิ่มรายการเคลมใหม่"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            branch = st.selectbox("สาขา", branches)
            counter = st.text_input("Counter")
            sn_faulty = st.text_input("Serial เครื่องที่เสีย (บังคับ)")
            sn_to_center = st.text_input("Serial เครื่องที่ส่งให้ศูนย์")
        with col2:
            status = st.selectbox("แก้ในTrackMo (สถานะ)", ["Pending", "inprogress", "Done"])
            date_claim = st.date_input("วันที่ส่งเคลม", value=None)
            date_install = st.date_input("วันที่นำไปติดตั้งใหม่", value=None)
            sn_new = st.text_input("Serial เครื่องที่เปลี่ยนใหม่")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not sn_faulty:
                st.warning("⚠️ กรุณากรอก Serial เครื่องที่เสีย")
            else:
                # แปลงวันที่จาก date picker เป็น string format
                str_date_claim = date_claim.strftime("%Y-%m-%d") if date_claim else ""
                str_date_install = date_install.strftime("%Y-%m-%d") if date_install else ""
                
                new_row = pd.DataFrame([{
                    "วันที่รับแจ้ง": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "วันที่ส่งเคลม": str_date_claim,
                    "วันทีนำไปติดตั้งใหม่": str_date_install,
                    "สาขา": branch,
                    "counter": counter,
                    "Serial เครื่องที่เสีย": sn_faulty,
                    "Serial เครื่องที่ส่งให้ศูนย์": sn_to_center,
                    "Serial เครื่องที่เปลี่ยนใหม่": sn_new,
                    "แก้ในTrackMo": status
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # รักษาลำดับคอลัมน์มาตรฐานไว้
                updated_df = updated_df[EXPECTED_COLUMNS]
                conn.update(data=updated_df)
                st.success("✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ระบบค้นหาและตัวกรอง ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")
search_col1, search_col2 = st.columns([2, 1])

with search_col1:
    search_query = st.text_input("🔎 ค้นหาจาก Serial, Counter หรือชื่อสาขา", placeholder="พิมพ์คำค้นหา...")

with search_col2:
    # ค้นหาตามสาขาแทนเนื่องจากตารางใหม่ไม่มีประเภทอุปกรณ์แล้ว
    options = ["ทั้งหมด"] + sorted(df["สาขา"].dropna().unique().tolist()) if not df.empty else ["ทั้งหมด"]
    filter_branch = st.selectbox("🏷️ กรองตามสาขา", options)

# Logic การกรองข้อมูล
view_df = df.copy()
if filter_branch != "ทั้งหมด":
    view_df = view_df[view_df["สาขา"] == filter_branch]

if search_query:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

# --- ส่วนที่ 4: แสดงผลและแก้ไขข้อมูล ---
if not view_df.empty:
    st.write(f"พบข้อมูล {len(view_df)} รายการ")
    st.dataframe(view_df, use_container_width=True, hide_index=True)

    with st.expander("📝 แก้ไขข้อมูลสถานะหรือเครื่องที่เปลี่ยนใหม่"):
        # อิงตามฟิลด์ Serial เครื่องที่เสีย
        valid_sn_list = view_df["Serial เครื่องที่เสีย"].dropna().unique().tolist()
        selected_sn = st.selectbox("เลือก Serial เครื่องที่เสีย ที่ต้องการแก้ไข", valid_sn_list)
        
        if selected_sn:
            target_data = df[df["Serial เครื่องที่เสีย"] == selected_sn].iloc[0]
            
            with st.form("edit_form"):
                edit_col1, edit_col2 = st.columns(2)
                with edit_col1:
                    current_status = str(target_data["แก้ในTrackMo"]).strip()
                    status_options = ["Pending", "inprogress", "Done"]
                    try:
                        status_idx = status_options.index(current_status)
                    except:
                        status_idx = 0
                        
                    new_status = st.selectbox("อัปเดตสถานะใน TrackMo", status_options, index=status_idx)
                    new_sn_to_center = st.text_input("อัปเดต Serial ส่งให้ศูนย์", value=str(target_data["Serial เครื่องที่ส่งให้ศูนย์"]))
                with edit_col2:
                    new_sn_new = st.text_input("อัปเดต Serial เครื่องที่เปลี่ยนใหม่", value=str(target_data["Serial เครื่องที่เปลี่ยนใหม่"]))
                    
                    # ตัวเลือกแก้ไขวันที่นำไปติดตั้งใหม่
                    current_install_date = None
                    if pd.notna(target_data["วันทีนำไปติดตั้งใหม่"]) and str(target_data["วันทีนำไปติดตั้งใหม่"]).strip() != "":
                        try:
                            current_install_date = datetime.strptime(str(target_data["วันทีนำไปติดตั้งใหม่"]).strip(), "%Y-%m-%d").date()
                        except:
                            pass
                    new_date_install = st.date_input("อัปเดต วันที่นำไปติดตั้งใหม่", value=current_install_date)
                
                if st.form_submit_button("ยืนยันการแก้ไข"):
                    idx = df.index[df["Serial เครื่องที่เสีย"] == selected_sn].tolist()[0]
                    
                    df.at[idx, "แก้ในTrackMo"] = new_status
                    df.at[idx, "Serial เครื่องที่ส่งให้ศูนย์"] = new_sn_to_center
                    df.at[idx, "Serial เครื่องที่เปลี่ยนใหม่"] = new_sn_new
                    df.at[idx, "วันทีนำไปติดตั้งใหม่"] = new_date_install.strftime("%Y-%m-%d") if new_date_install else ""
                    
                    # รักษารูปแบบโครงสร้างคอลัมน์มาตรฐานก่อนอัปเดตลง Sheet
                    df = df[EXPECTED_COLUMNS]
                    conn.update(data=df)
                    st.success(f"อัปเดต Serial {selected_sn} เรียบร้อย!")
                    st.rerun()

    # ปุ่มดาวน์โหลด
    csv = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลด CSV", csv, "claim_report.csv", "text/csv")
else:
    st.info("💡 ไม่พบข้อมูลที่ตรงตามเงื่อนไข")
