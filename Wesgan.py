import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import io

# ซ่อนเมนูเดิม
st.markdown("### ระบบจัดการทรัพย์สิน (Asset System)")

# --- 1. เชื่อมต่อฐานข้อมูล ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลหลักได้")
    st.stop()

# --- 2. กำหนดโครงสร้างข้อมูล ---
ASSET_COLUMNS = ["Serial Number (เลขซีเรียล)", "Model Name (ชื่อรุ่น)", "Location (สถานที่)", "วันที่ซื้อ"]

# --- 3. ดึงข้อมูล ---
try:
    df = conn.read(worksheet="Asset Management", ttl="0")
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip()
        # ตรวจสอบคอลัมน์ให้ครบ
        for col in ASSET_COLUMNS:
            if col not in df.columns: df[col] = ""
        df = df[ASSET_COLUMNS]
    else:
        df = pd.DataFrame(columns=ASSET_COLUMNS)
except:
    df = pd.DataFrame(columns=ASSET_COLUMNS)

# --- 4. จัดการ State สำหรับการแก้ไข ---
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None
if "row_index" not in st.session_state:
    st.session_state.row_index = None

def reset_edit_state():
    st.session_state.edit_data = None
    st.session_state.row_index = None

# --- 5. Sidebar & Filtering ---
    st.subheader("🎯 ตัวกรอง Model")
    all_models = ["ทั้งหมด"] + sorted(df["Model Name (ชื่อรุ่น)"].unique().tolist())
    filter_model = st.selectbox("เลือกดูเฉพาะรุ่น:", all_models)

# กรองข้อมูลตาม Sidebar
view_df = df.copy()
if filter_model != "ทั้งหมด":
    view_df = view_df[view_df["Model Name (ชื่อรุ่น)"] == filter_model]

# --- 6. UI หลัก (Form สำหรับเพิ่ม/แก้ไขข้อมูลหลัก) ---
st.title("🛡️ Asset Management")

is_editing = st.session_state.edit_data is not None
expander_label = "📝 แก้ไขข้อมูลทรัพย์สิน" if is_editing else "➕ ลงทะเบียนทรัพย์สินใหม่"

with st.expander(expander_label, expanded=is_editing):
    with st.form("asset_form", clear_on_submit=True):
        current_val = st.session_state.edit_data if is_editing else {}
        
        col1, col2 = st.columns(2)
        with col1:
            input_sn = st.text_input("Serial Number", value=current_val.get("Serial Number (เลขซีเรียล)", ""))
            input_model = st.text_input("Model Name", value=current_val.get("Model Name (ชื่อรุ่น)", ""))
        with col2:
            input_loc = st.text_input("Location", value=current_val.get("Location (สถานที่)", ""))
            
            try:
                if is_editing and current_val.get("วันที่ซื้อ"):
                    default_date = datetime.strptime(current_val.get("วันที่ซื้อ"), "%d-%m-%Y")
                else:
                    default_date = datetime.now()
            except:
                default_date = datetime.now()
            
            input_date = st.date_input("วันที่ซื้อ", value=default_date, format="DD/MM/YYYY")
        
        b_col1, b_col2 = st.columns([1, 5])
        with b_col1:
            submit = st.form_submit_button("💾 บันทึก")
        with b_col2:
            if is_editing:
                if st.form_submit_button("❌ ยกเลิกการแก้ไข"):
                    reset_edit_state()
                    st.rerun()

        if submit:
            if input_sn:
                updated_row_data = {
                    "Serial Number (เลขซีเรียล)": str(input_sn),
                    "Model Name (ชื่อรุ่น)": str(input_model),
                    "Location (สถานที่)": str(input_loc),
                    "วันที่ซื้อ": input_date.strftime("%d-%m-%Y"),
                }
                
                try:
                    if is_editing:
                        df.iloc[st.session_state.row_index] = updated_row_data
                        success_msg = "อัปเดตข้อมูลเรียบร้อยแล้ว!"
                    else:
                        new_row_df = pd.DataFrame([updated_row_data])
                        df = pd.concat([df, new_row_df], ignore_index=True)
                        success_msg = "ลงทะเบียนใหม่เรียบร้อยแล้ว!"
                    
                    conn.update(worksheet="Asset Management", data=df.astype(str))
                    st.success(success_msg)
                    reset_edit_state()
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
            else:
                st.error("กรุณาระบุ Serial Number")

# --- 7. ส่วนแสดงผลตารางและแก้ไขสถานที่ (Update ส่วนนี้) ---
st.divider()
c1, c2 = st.columns([3, 1])

with c1:
    search_term = st.text_input("🔍 ค้นหาในตาราง (S/N, รุ่น, สถานที่):")
    if search_term:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        view_df = view_df[mask]

with c2:
    st.write("📊 Report")
    csv_data = view_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"Asset_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.write(f"พบข้อมูลทั้งหมด: **{len(view_df)}** รายการ (คลิกที่ช่องสถานที่เพื่อแก้ไขได้ทันที)")

# ใช้ data_editor เพื่อให้แก้ไข Location ได้
edited_view_df = st.data_editor(
    view_df,
    use_container_width=True,
    hide_index=False,
    column_config={
        "Serial Number (เลขซีเรียล)": st.column_config.TextColumn(disabled=True),
        "Model Name (ชื่อรุ่น)": st.column_config.TextColumn(disabled=True),
        "วันที่ซื้อ": st.column_config.TextColumn(disabled=True),
        "Location (สถานที่)": st.column_config.TextColumn(disabled=False) # เปิดให้แก้ได้
    },
    key="bulk_edit_location"
)

# ปุ่มบันทึกการแก้ไขสถานที่
if st.button("✅ ยืนยันการเปลี่ยนสถานที่ในตาราง"):
    try:
        # อัปเดตข้อมูลที่แก้กลับไปใน DataFrame หลัก
        df.update(edited_view_df)
        conn.update(worksheet="Asset Management", data=df.astype(str))
        st.success("บันทึกการเปลี่ยนสถานที่เรียบร้อย!")
        st.rerun()
    except Exception as e:
        st.error(f"ไม่สามารถบันทึกได้: {e}")
