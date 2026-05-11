import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Wesgan Asset", layout="wide")

# 2. Hide Default Nav
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("🎮 IT Management")
    st.page_link("app.py", label="JVFS Device Claim", icon="📑")
    st.page_link("pages/Wesgan.py", label="Wesgan Asset System", icon="🛡️")

# 4. Connection
try:
    conn = st.connection("gsheets_wesgan", type=GSheetsConnection)
except Exception as e:
    st.error("Connection Error: Check your Secrets")
    st.stop()

# 5. Column Definitions
COLS = ["AssetCode", "Serial", "ModelName", "AssetTypeName", "BrandName", "LocationName", "PurchaseDate", "PurchasePrice"]

# 6. Load Data
try:
    df = conn.read(worksheet="Sheet1", ttl="0")
    if df is None or df.empty:
        df = pd.DataFrame(columns=COLS)
    else:
        df = df.dropna(how='all') # ลบบรรทัดว่าง
except Exception:
    df = pd.DataFrame(columns=COLS)

st.title("🛡️ Wesgan Asset System")

# 7. Add Form
with st.expander("➕ เพิ่มทรัพย์สินใหม่"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        a_code = c1.text_input("AssetCode")
        a_sn = c1.text_input("Serial")
        a_model = c2.text_input("ModelName")
        a_type = c2.text_input("AssetTypeName")
        a_brand = c3.text_input("BrandName")
        a_loc = c3.text_input("LocationName")
        a_date = st.date_input("PurchaseDate")
        a_price = st.text_input("PurchasePrice", value="0")
        
        if st.form_submit_button("บันทึก"):
            if a_code:
                new_data = pd.DataFrame([{
                    "AssetCode": a_code, "Serial": a_sn, "ModelName": a_model,
                    "AssetTypeName": a_type, "BrandName": a_brand, "LocationName": a_loc,
                    "PurchaseDate": a_date.strftime("%Y-%m-%d"), "PurchasePrice": a_price
                }])
                updated_df = pd.concat([df, new_data], ignore_index=True).astype(str)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("บันทึกสำเร็จ!")
                st.rerun()
            else:
                st.error("ต้องระบุ AssetCode")

# 8. Display Table
st.divider()
st.subheader("🔍 รายการทรัพย์สิน")
st.dataframe(df, use_container_width=True, hide_index=True)
