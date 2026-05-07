import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Device Claim System", layout="wide")
st.title("🔌 ระบบบันทึกข้อมูลการเคลมอุปกรณ์")

# --- SIMULATED DATABASE (ในใช้งานจริงควรเชื่อมต่อกับ SQLite หรือ Supabase) ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        "วันที่แจ้ง", "ประเภทอุปกรณ์", "สาขา", "Asset No.", "S/N เครื่องเสีย", "อาการ", "สถานะ"
    ])

# --- SIDEBAR: Filter & Search ---
st.sidebar.header("🔍 ค้นหาและตัวกรอง")
search_query = st.sidebar.text_input("ค้นหา S/N หรือ Asset No.")
filter_type = st.sidebar.selectbox("กรองตามประเภท", ["ทั้งหมด", "Signature pad", "Monitor", "UPS", "CCTV"])

# --- FUNCTION: บันทึกข้อมูล ---
with st.expander("➕ เพิ่มรายการเคลมใหม่"):
    col1, col2 = st.columns(2)
    with col1:
        d_type = st.selectbox("ประเภทอุปกรณ์", ["Signature pad", "Monitor", "UPS", "Passport Scanner", "CCTV"])
        branch = st.text_input("สาขา")
        asset = st.text_input("Asset No.")
    with col2:
        sn_faulty = st.text_input("Serial Number เครื่องเสีย")
        symptom = st.text_area("อาการเสีย")
        status = st.selectbox("สถานะ", ["In Progress", "Done", "Pending"])
    
    if st.button("บันทึกข้อมูล"):
        new_data = {
            "วันที่แจ้ง": datetime.now().strftime("%Y-%m-%d"),
            "ประเภทอุปกรณ์": d_type,
            "สาขา": branch,
            "Asset No.": asset,
            "S/N เครื่องเสีย": sn_faulty,
            "อาการ": symptom,
            "สถานะ": status
        }
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
        st.success("บันทึกสำเร็จ!")

# --- MAIN: แสดงข้อมูลและรายงาน ---
st.subheader("📋 รายการข้อมูลทั้งหมด")

# ส่วนการกรองข้อมูล
display_df = st.session_state.db
if filter_type != "ทั้งหมด":
    display_df = display_df[display_df["ประเภทอุปกรณ์"] == filter_type]
if search_query:
    display_df = display_df[display_df["S/N เครื่องเสีย"].str.contains(search_query) | display_df["Asset No."].str.contains(search_query)]

st.dataframe(display_df, use_container_width=True)

# --- FUNCTION: ดึง Report ---
st.subheader("📊 Report")
if not display_df.empty:
    csv = display_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="📥 Download Report (CSV)",
        data=csv,
        file_name=f"device_claim_report_{datetime.now().date()}.csv",
        mime="text/csv",
    )
else:
    st.info("ยังไม่มีข้อมูลสำหรับออกรายงาน")
