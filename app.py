import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="JVFS Device Claim System", layout="wide")

# 1. เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลหลัก
try:
    df = conn.read(ttl="0")
    # ตรวจสอบว่ามีข้อมูลไหม ถ้าไม่มีให้สร้าง DataFrame เปล่าที่มี Column ครบ
    if df is None or df.empty:
        df = pd.DataFrame(columns=["วันที่บันทึก", "ประเภทอุปกรณ์", "สาขา", "Asset No.", "S/N เครื่องเสีย", "อาการเสีย", "สถานะ", "S/N เครื่องใหม่"])
except Exception:
    st.error("❌ ไม่พบการตั้งค่า Spreadsheet! กรุณาตรวจสอบลิงก์ใน Secrets")
    st.stop()

# ข้อมูลสำหรับ Dropdown
branches = ["One Bangkok", "กรุงเทพฯ 1", "กรุงเทพฯ 2", "นนทบุรี", "สมุทรสาคร", "เชียงใหม่", "ตาก", "สงขลา"]
device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Monitor Dell", "Dell Pro Tower", "CCTV", "TV Samsung"
]

st.title("📑 JVFS Device Claim System")

# --- ส่วนที่ 1: Dashboard สรุปผล (ใหม่ ✨) ---
if not df.empty:
    st.subheader("📊 ภาพรวมการเคลม")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายการทั้งหมด", len(df))
    m2.metric("รอดำเนินการ (Pending)", len(df[df["สถานะ"] == "Pending"]))
    m3.metric("กำลังทำ (In Progress)", len(df[df["สถานะ"] == "inprogress"]))
    m4.metric("เสร็จสิ้น (Done)", len(df[df["สถานะ"] == "Done"]))
    st.divider()

# --- ส่วนที่ 2: ฟอร์มบันทึกข้อมูล ---
with st.expander("➕ เพิ่มรายการเคลมใหม่"):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("ประเภทอุปกรณ์", device_types)
            branch = st.selectbox("สาขา", branches)
            asset_no = st.text_input("Asset No.")
            sn_faulty = st.text_input("S/N เครื่องที่เสีย")
        with col2:
            status = st.selectbox("สถานะ", ["Pending", "inprogress", "Done"])
            symptom = st.text_area("อาการเสีย")
            sn_new = st.text_input("S/N เครื่องใหม่ (ถ้ามี)")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            if not asset_no or not sn_faulty:
                st.warning("⚠️ กรุณากรอก Asset No. และ S/N เครื่องเสีย")
            else:
                new_row = pd.DataFrame([{
                    "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "ประเภทอุปกรณ์": category,
                    "สาขา": branch,
                    "Asset No.": asset_no,
                    "S/N เครื่องเสีย": sn_faulty,
                    "อาการเสีย": symptom,
                    "สถานะ": status,
                    "S/N เครื่องใหม่": sn_new
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("✅ บันทึกสำเร็จ!")
                st.rerun()

# --- ส่วนที่ 3: ระบบค้นหาและตัวกรอง ---
st.subheader("🔍 ค้นหาและตรวจสอบข้อมูล")
search_col1, search_col2 = st.columns([2, 1])

with search_col1:
    search_query = st.text_input("🔎 ค้นหาจาก S/N, Asset No, หรือชื่อสาขา", placeholder="พิมพ์เพื่อค้นหา...")

with search_col2:
    if not df.empty:
        options = ["ทั้งหมด"] + sorted(df["ประเภทอุปกรณ์"].unique().tolist())
    else:
        options = ["ทั้งหมด"]
    filter_cat = st.selectbox("🏷️ เลือกประเภทอุปกรณ์", options)

# Logic การกรองข้อมูล
view_df = df.copy()
if filter_cat != "ทั้งหมด":
    view_df = view_df[view_df["ประเภทอุปกรณ์"] == filter_cat]

if search_query:
    mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    view_df = view_df[mask]

# --- ส่วนที่ 4: แสดงผลและแก้ไขข้อมูล (ใหม่ ✨) ---
if not view_df.empty:
    st.write(f"พบข้อมูล {len(view_df)} รายการ")
    
    # แสดงตาราง
    st.dataframe(view_df, use_container_width=True, hide_index=True)

    # ฟีเจอร์แก้ไขข้อมูล
    with st.expander("📝 แก้ไขสถานะหรือข้อมูลเครื่องใหม่"):
        st.info("เลือกรายการจาก S/N เครื่องเสีย เพื่อทำการอัปเดตข้อมูล")
        selected_sn = st.selectbox("เลือก S/N ที่ต้องการแก้ไข", view_df["S/N เครื่องเสีย"].tolist())
        
        # ดึงข้อมูลเดิมมาแสดงในฟอร์มแก้ไข
        edit_data = df[df["S/N เครื่องเสีย"] == selected_sn].iloc[0]
        
        with st.form("edit_form"):
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                new_status = st.selectbox("อัปเดตสถานะ", ["Pending", "inprogress", "Done"], 
                                         index=["Pending", "inprogress", "Done"].index(edit_data["สถานะ"]))
            with edit_col2:
                new_sn_new = st.text_input("อัปเดต S/N เครื่องใหม่", value=edit_data["S/N เครื่องใหม่"])
            
            if st.form_submit_button("ยืนยันการแก้ไข"):
                # ค้นหาตำแหน่ง Index จริงใน df หลัก
                target_idx = df.index[df["S/N เครื่องเสีย"] == selected_sn].tolist()[0]
                df.at[target_idx, "สถานะ"] = new_status
                df.at[target_idx, "S/N เครื่องใหม่"] = new_sn_new
                
                conn.update(data=df)
                st.success(f"อัปเดต S/N {selected_sn} เรียบร้อยแล้ว!")
                st.rerun()

    # ปุ่มดาวน์โหลด
    csv = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลดรายการที่กรองแล้ว (CSV)", csv, "claim_report.csv", "text/csv")
else:
    st.info("💡 ยังไม่มีข้อมูลที่ตรงตามเงื่อนไข")
