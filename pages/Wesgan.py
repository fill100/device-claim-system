import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Asset Management", layout="wide")

# ซ่อนเมนูเดิม
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# 1. เชื่อมต่อฐานข้อมูล
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# 2. กำหนดหัวข้อคอลัมน์
ASSET_COLUMNS = ["Serial Number (เลขซีเรียล)", "Model Name (ชื่อรุ่น)", "Location (สถานที่)", "วันที่ซื้อ"]

# 3. ดึงข้อมูล
try:
    df = conn.read(worksheet="Asset Management", ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        for col in ASSET_COLUMNS:
            if col not in df.columns: df[col] = ""
        df = df[ASSET_COLUMNS]
    else:
        df = pd.DataFrame(columns=ASSET_COLUMNS)
except:
    df = pd.DataFrame(columns=ASSET_COLUMNS)

# 4. Sidebar & Filtering
with st.sidebar:
    st.markdown("# 💻 IT Management")
    st.page_link("app.py", label="Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Asset System", icon="🛡️")
    st.divider()
    
    st.subheader("🎯 ตัวกรองข้อมูล")
    all_models = ["ทั้งหมด"] + sorted(df["Model Name (ชื่อรุ่น)"].unique().tolist())
    filter_model = st.selectbox("เลือก Model Name:", all_models)

# 5. การกรองข้อมูลสำหรับการแสดงผลและ Report
view_df = df.copy()
if filter_model != "ทั้งหมด":
    view_df = view_df[view_df["Model Name (ชื่อรุ่น)"] == filter_model]

# 6. UI หลัก
st.title("🛡️ Asset Management")

# --- ส่วนของการแก้ไขข้อมูล (State Management) ---
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ฟังก์ชันสำหรับรีเซ็ตฟอร์ม
def reset_edit():
    st.session_state.edit_index = None
    st.rerun()

# --- ฟอร์มลงทะเบียน / แก้ไข ---
expander_label = "📝 แก้ไขข้อมูลทรัพย์สิน" if st.session_state.edit_index is not None else "➕ ลงทะเบียนทรัพย์สินใหม่"
with st.expander(expander_label, expanded=(st.session_state.edit_index is not None)):
    with st.form("asset_form", clear_on_submit=True):
        # ดึงค่าเริ่มต้นถ้าอยู่ในโหมดแก้ไข
        default_val = {"sn": "", "model": "", "loc": "", "date": datetime.now()}
        if st.session_state.edit_index is not None:
            row = df.iloc[st.session_state.edit_index]
            default_val["sn"] = row["Serial Number (เลขซีเรียล)"]
            default_val["model"] = row["Model Name (ชื่อรุ่น)"]
            default_val["loc"] = row["Location (สถานที่)"]
            try:
                default_val["date"] = datetime.strptime(row["วันที่ซื้อ"], "%d-%m-%Y")
            except:
                default_val["date"] = datetime.now()

        col1, col2 = st.columns(2)
        with col1:
            input_sn = st.text_input("Serial Number (เลขซีเรียล)", value=default_val["sn"])
            input_model = st.text_input("Model Name (ชื่อรุ่น)", value=default_val["model"])
        with col2:
            input_loc = st.text_input("Location (สถานที่)", value=default_val["loc"])
            input_date = st.date_input("วันที่ซื้อ", value=default_val["date"], format="DD/MM/YYYY")
        
        btn_col1, btn_col2 = st.columns([1, 5])
        with btn_col1:
            submit = st.form_submit_button("💾 บันทึก")
        with btn_col2:
            if st.session_state.edit_index is not None:
                if st.form_submit_button("❌ ยกเลิกแก้ไข"):
                    reset_edit()

        if submit:
            if input_sn:
                new_data = {
                    "Serial Number (เลขซีเรียล)": str(input_sn),
                    "Model Name (ชื่อรุ่น)": str(input_model),
                    "Location (สถานที่)": str(input_loc),
                    "วันที่ซื้อ": input_date.strftime("%d-%m-%Y"),
                }
                
                try:
                    if st.session_state.edit_index is not None:
                        # กรณีแก้ไข: แทนที่บรรทัดเดิม
                        df.iloc[st.session_state.edit_index] = new_data
                        msg = "อัปเดตข้อมูลสำเร็จ!"
                    else:
                        # กรณีเพิ่มใหม่: ต่อท้าย
                        new_row = pd.DataFrame([new_data])
                        df = pd.concat([df, new_row], ignore_index=True)
                        msg = "บันทึกข้อมูลใหม่สำเร็จ!"
                    
                    conn.update(worksheet="Asset Management", data=df.astype(str))
                    st.success(msg)
                    st.session_state.edit_index = None
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
            else:
                st.error("กรุณาระบุ Serial Number")

# --- ส่วน Report & Search ---
st.divider()
c1, c2 = st.columns([3, 1])

with c1:
    search = st.text_input("🔍 ค้นหาในตาราง:")
    if search:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        view_df = view_df[mask]

with c2:
    # ปุ่มดึง Report เป็น CSV (ไม่ต้องลง xlsxwriter เพิ่ม)
    st.write("📊 Report")
    csv = view_df.to_csv(index=False).encode('utf-8-sig') # utf-8-sig เพื่อให้ภาษาไทยไม่ต่าง
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"Asset_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# --- ตารางแสดงผลพร้อมปุ่มแก้ไข ---
st.write(f"แสดงข้อมูล: **{filter_model}** ({len(view_df)} รายการ)")

# ใช้ st.data_editor หรือสร้างปุ่มจำลองการเลือกแก้ไข
event = st.dataframe(
    view_df, 
    use_container_width=True, 
    hide_index=False, # เปิด Index ไว้เพื่อให้ระบุแถวที่จะแก้ไขได้ง่าย
    on_select="rerun",
    selection_mode="single-row"
)

# ตรวจสอบการเลือกแถวในตารางเพื่อแก้ไข
if len(event.selection.rows) > 0:
    selected_row_index = event.selection.rows[0]
    # หา index จริงใน df หลักจาก view_df
    actual_index = view_df.index[selected_row_index]
    st.session_state.edit_index = actual_index
    st.info(f"เลือกรายการ S/N: {df.iloc[actual_index]['Serial Number (เลขซีเรียล)']} แล้ว กรุณาเลื่อนขึ้นไปแก้ไขที่ฟอร์มด้านบน")
    st.rerun()
