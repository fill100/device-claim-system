import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าพื้นฐานของโปรแกรม (ต้องอยู่บรรทัดแรกสุด)
st.set_page_config(page_title="JVFS Device Claim & Logistics", layout="wide")

# 2. ฟังก์ชันแชร์สิทธิ์การเชื่อมต่อฐานข้อมูล Google Sheets
def get_sheets_connection():
    if "connections" not in st.secrets:
        st.error("❌ ไม่พบโครงสร้าง Secrets กรุณาตั้งค่า Spreadsheet URL ก่อนครับ")
        st.stop()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception:
        st.error("❌ ไม่สามารถเชื่อมต่อกับ Google Sheets ได้")
        st.stop()

# ฐานข้อมูลสาขาจากไฟล์ของคุณ
branches_list = [
    "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", 
    "กรุงเทพมหานคร 5 (สจก.9)", "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)",
    "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", "สมุทรสาคร", "สมุทรปราการ", "นครปฐม",
    "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", "สระบุรี", "สุพรรณบุรี",
    "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", "จันทบุรี",
    "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร",
    "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี",
    "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง",
    "ระนอง", "สงขลา", "สุราษฎร์ธานี", "กระบี่"
]

device_types = [
    "Signature pad", "Passport Scanner", "Iris Scanner", "Printer Thermal (ปริ้นคิว)",
    "Printer Pantum", "Honeywell g1950", "Newland HR2000", "UPS ประจำศูนย์",
    "Android Box", "Adapter Android Box", "Monitor", "PC", "CCTV", "TV"
]

# =====================================================================
# 🛠️ ฟังก์ชันของหน้าต่างแต่ละหน้า (จับแยกกลุ่มชัดเจน)
# =====================================================================

# [หน้าหลัก 1] หน้าภาพรวมระบบงานเคลม
def claim_dashboard():
    st.title("📊 ภาพรวมระบบงานเคลม (Dashboard)")
    st.write("ยินดีต้อนรับสู่ระบบ JVFS Device Claim System ส่วนนี้คือหน้าหลักสำหรับดูภาพรวมครับ")
    # คุณสามารถเพิ่มกราฟสรุป หรือสรุปยอด Pending/inprogress/Done ตรงนี้ได้ในอนาคต

# [หน้ารอง 1-1] บันทึกและติดตามงานเคลม
def claim_system_page():
    st.title("📑 บันทึกและติดตามงานเคลม")
    st.caption("ระบบบันทึก ตรวจสอบ และติดตามสถานะการเคลมอุปกรณ์ไอทีประจำศูนย์บริการ")
    
    conn = get_sheets_connection()
    df = conn.read(ttl="0")

    with st.expander("➕ เพิ่มรายการเคลมใหม่", expanded=False):
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("ประเภทอุปกรณ์", device_types)
                branch = st.selectbox("สาขาที่พบปัญหา", branches_list)
                asset_no = st.text_input("Asset No.")
                sn_faulty = st.text_input("S/N เครื่องที่เสีย")
            with col2:
                status = st.selectbox("สถานะปัจจุบัน", ["Pending", "inprogress", "Done"])
                symptom = st.text_area("อาการเสียโดยละเอียด")
                sn_new = st.text_input("S/N เครื่องใหม่ / ของเปลี่ยนทดแทน")
            
            if st.form_submit_button("💾 บันทึกข้อมูลลง Google Sheets"):
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
                st.success("✅ อัปเดตข้อมูลเข้าฐานข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

    st.divider()
    st.subheader("🔍 ค้นหาและคัดกรองข้อมูล")
    search_col1, search_col2 = st.columns([2, 1])
    with search_col1:
        search_query = st.text_input("🔎 พิมพ์คำค้นหา (เช่น S/N, Asset, ชื่อจังหวัด...)", placeholder="พิมพ์เพื่อสแกนหาคำ...")
    with search_col2:
        options = ["ทั้งหมด"] + sorted(df["ประเภทอุปกรณ์"].unique().tolist()) if not df.empty else ["ทั้งหมด"]
        filter_cat = st.selectbox("🏷️ เลือกเฉพาะอุปกรณ์", options)

    view_df = df.copy()
    if filter_cat != "ทั้งหมด":
        view_df = view_df[view_df["ประเภทอุปกรณ์"] == filter_cat]
    if search_query:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        view_df = view_df[mask]

    if not view_df.empty:
        st.write(f"📊 พบผลลัพธ์ข้อมูลทั้งหมด {len(view_df)} รายการ")
        st.dataframe(view_df, use_container_width=True, hide_index=True)
    else:
        st.info("💡 ไม่พบข้อมูลตามเงื่อนไข")


# [หน้าหลัก 2] หน้าภาพรวมระบบจัดส่ง
def logistics_dashboard():
    st.title("🚚 ภาพรวมระบบงานจัดส่ง (Logistics Dashboard)")
    st.write("ส่วนงานจัดการคลังสินค้า พัสดุ และการขนส่งอุปกรณ์เคลมไปยังศูนย์บริการต่างๆ")


# [หน้ารอง 2-1] ออกใบปะหน้าพัสดุ & ข้อมูลศูนย์ฯ
def shipping_label_page():
    st.title("📦 ข้อมูลที่อยู่ศูนย์ฯ & ใบปะหน้า")
    
    tab1, tab2 = st.tabs(["🖨️ ออกใบปะหน้าพัสดุ", "🏠 รายชื่อศูนย์บริการ"])
    with tab1:
        st.subheader("📋 รายละเอียดพัสดุจัดส่ง")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 👤 **ผู้ส่ง (From)**")
            s_name = st.text_input("ชื่อผู้ส่ง / ฝ่ายงาน", value="แผนก IT - JVFS สำนักงานใหญ่")
            s_branch = st.selectbox("จากสาขา/คลัง", ["สำนักงานใหญ่ (HQ)"] + branches_list)
            s_addr = st.text_area("ที่อยู่จัดส่งต้นทาง", value="อาคาร JVFS เลขที่... แขวง... เขต... กรุงเทพฯ 10xxx", height=80)
            s_phone = st.text_input("เบอร์โทรศัพท์ผู้ส่ง", value="02-XXX-XXXX")
        with c2:
            st.markdown("#### 📍 **ผู้รับ (To)**")
            r_name = st.text_input("ชื่อผู้รับ / เจ้าหน้าที่", value="เจ้าหน้าที่ปฏิบัติงานประจำศูนย์บริการ")
            r_branch = st.selectbox("ปลายทางศูนย์บริการ", branches_list)
            r_addr = st.text_area("ที่อยู่จัดส่งปลายทาง", placeholder="กรุณาระบุที่อยู่จัดส่งจริง...", height=80)
            r_phone = st.text_input("เบอร์โทรศัพท์ผู้รับ", placeholder="เช่น 08X-XXX-XXXX")
            
        st.divider()
        label_html = f"""
        <div style="border: 3px dashed #1e3a8a; padding: 25px; border-radius: 12px; background-color: #fff; color: #111; font-family: sans-serif;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 45%; border-right: 2px solid #e5e7eb; padding-right: 20px; vertical-align: top;">
                        <span style="background-color: #6b7280; color: #fff; padding: 4px 10px; font-size: 11px; font-weight: bold; border-radius: 4px;">Sender (ผู้ส่ง)</span>
                        <p style="margin-top: 12px; font-size: 13px;"><b>{s_name}</b><br>สาขา: {s_branch}<br>ที่อยู่: {s_addr}<br><b>โทร: {s_phone}</b></p>
                    </td>
                    <td style="width: 55%; padding-left: 20px; vertical-align: top;">
                        <span style="background-color: #16a34a; color: #fff; padding: 4px 10px; font-size: 12px; font-weight: bold; border-radius: 4px;">Receiver (ผู้รับ)</span>
                        <p style="margin-top: 12px; font-size: 16px;">📍 <b>ศูนย์บริการ: {r_branch}</b><br><b>ชื่อผู้รับ:</b> {r_name}<br><b>ที่อยู่:</b> {r_addr}<br>📞 <b>โทร: {r_phone}</b></p>
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(label_html, unsafe_allow_html=True)

    with tab2:
        st.subheader("🏠 ทำเนียบข้อมูลศูนย์บริการทั้งหมด")
        b_search = st.text_input("🔍 ค้นหาจังหวัดหรือชื่อศูนย์", placeholder="พิมพ์ชื่อศูนย์...")
        master_branch_df = pd.DataFrame({"ลำดับที่": range(1, len(branches_list) + 1), "ชื่อศูนย์บริการ": branches_list})
        if b_search:
            master_branch_df = master_branch_df[master_branch_df["ชื่อศูนย์บริการ"].str.contains(b_search, case=False)]
        st.dataframe(master_branch_df, use_container_width=True, hide_index=True)


# =====================================================================
# 🗂️ การตั้งค่าโครงสร้างเมนูแบบ หน้าหลัก -> หน้ารอง (Hierarchical Routing)
# =====================================================================

# กำหนดหน้าต่างๆ แปลงเป็น วัตถุหน้าเพจของ Streamlit
page_claim_main = st.Page(claim_dashboard, title="ระบบงานเคลมอุปกรณ์", icon="📊", default=True)
page_claim_sub1 = st.Page(claim_system_page, title="└─ บันทึกและติดตามงานเคลม", icon="📑")

page_ship_main = st.Page(logistics_dashboard, title="ระบบงานจัดส่งพัสดุ", icon="🚚")
page_ship_sub1 = st.Page(shipping_label_page, title="└─ ที่อยู่ศูนย์ฯ & ใบปะหน้า", icon="📦")

# มัดรวมกิ่งก้านหน้าเพจเข้าด้วยกันตามแบบฉบับที่คุณต้องการในรูปภาพ
pg = st.navigation({
    "Claim Management": [page_claim_main, page_claim_sub1],
    "Logistics Management": [page_ship_main, page_ship_sub1]
})

# สั่งทำงานระบบโครงสร้างเมนูแบบแตกกิ่งก้าน
pg.run()
