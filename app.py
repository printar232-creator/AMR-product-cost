import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (4 Criteria - Smart Match)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ **เวอร์ชันแก้ไขปัญหาจับคู่ไม่เจอ (Not Found)**
โดยระบบจะสแกนหาและจับคู่จาก 4 หัวข้อหลักให้อัตโนมัติ:
1. **TYPE OF PRODUCT** | 2. **PACKAGING** | 3. **MATERIAL** | 4. **RATIO**
""")

st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

def find_smart_column(df_columns, target_keywords):
    for col in df_columns:
        col_clean = str(col).strip().upper().replace(" ", "").replace("_", "").replace("-", "")
        for kw in target_keywords:
            if kw in col_clean:
                return col
    return None

# ฟังก์ชันพิเศษในการทำความสะอาดข้อมูลขั้นสุดเพื่อลดโอกาสเกิด Not Found
def normalize_series(series):
    return series.astype(str).str.strip().str.upper()\
                 .str.replace(" ", "", regex=False)\
                 .str.replace("-", "", regex=False)\
                 .str.replace("_", "", regex=False)\
                 .str.replace(".", "", regex=False)\
                 .str.replace("/", "", regex=False)

if db_file and curr_file:
    df_db = pd.read_excel(db_file)
    df_curr = pd.read_excel(curr_file)
    
    type_kws = ["TYPEOFPRODUCT", "PRODUCTTYPE", "PRODUCT", "ประเภทสินค้า", "ชนิดสินค้า"]
    pkg_kws = ["PACKAGING", "PKG", "PACKAGE", "บรรจุภัณฑ์", "แพ็คเกจ", "ถุง"]
    mat_kws = ["MATERIAL", "MAT", "GRADE", "วัสดุ", "เกรด"]
    ratio_kws = ["RATIO", "อัตราส่วน", "สัดส่วน", "เปอร์เซ็นต์", "MESH"]
    price_kws = ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]

    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_ratio_col = find_smart_column(df_db.columns, ratio_kws)
    db_price_col = find_smart_column(df_db.columns, price_kws)

    curr_type_col = find_smart_column(df_curr.columns, type_kws)
    curr_pkg_col = find_smart_column(df_curr.columns, pkg_kws)
    curr_mat_col = find_smart_column(df_curr.columns, mat_kws)
    curr_ratio_col = find_smart_column(df_curr.columns, ratio_kws)

    st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด (ระบบตรวจจับคอลัมน์อัตโนมัติ 4 เงื่อนไข)")
    
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_ratio_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col and curr_ratio_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database) มีทั้งหมด: {len(df_db)} แถว**")
        if db_ready:
            st.success(f"🔍 พบคอลัมน์หลัก:\n- ประเภท=`{db_type_col}`\n- บรรจุภัณฑ์=`{db_pkg_col}`\n- วัสดุ=`{db_mat_col}`\n- อัตราส่วน=`{db_ratio_col}`\n- ราคา=`{db_price_col}`")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_db)
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา มีทั้งหมด: {len(df_curr)} แถว**")
        if curr_ready:
            st.success(f"🔍 พบคอลัมน์หลัก:\n- ประเภท=`{curr_type_col}`\n- บรรจุภัณฑ์=`{curr_pkg_col}`\n- วัสดุ=`{curr_mat_col}`\n- อัตราส่วน=`{curr_ratio_col}`")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_curr)

    if not db_ready or not curr_ready:
        st.warning("⚠️ โปรดตรวจสอบคอลัมน์ของทั้ง 2 ไฟล์ให้ถูกต้องก่อนรันระบบครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Smart Auto-Match)"):
            
            db_working = df_db.copy()
            curr_working = df_curr.copy()
            
            # เก็บข้อมูลเวอร์ชันดั้งเดิมของไฟล์ปัจจุบันไว้ เพื่อใช้แสดงผลในไฟล์ดาวน์โหลดตอนท้าย
            df_final_output = df_curr.copy()
            
            # สร้าง "คีย์ชั่วคราวสำหรับจับคู่" โดยล้างเครื่องหมาย เว้นวรรค ตัวเล็กตัวใหญ่ออกให้หมด
            db_working["join_type"] = normalize_series(db_working[db_type_col])
            db_working["join_pkg"] = normalize_series(db_working[db_pkg_col])
            db_working["join_mat"] = normalize_series(db_working[db_mat_col])
            db_working["join_ratio"] = normalize_series(db_working[db_ratio_col])
            
            df_final_output["join_type"] = normalize_series(df_final_output[curr_type_col])
            df_final_output["join_pkg"] = normalize_series(df_final_output[curr_pkg_col])
            df_final_output["join_mat"] = normalize_series(df_final_output[curr_mat_col])
            df_final_output["join_ratio"] = normalize_series(df_final_output[curr_ratio_col])
            
            # นิยามคีย์เชื่อม
            match_keys = ["join_type", "join_pkg", "join_mat", "join_ratio"]
            
            # ดึงราคารายการล่าสุดของแต่ละเงื่อนไขและลบตัวซ้ำใน DB
            df_db_prices = db_working[match_keys + [db_price_col]].drop_duplicates(subset=match
