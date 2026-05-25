import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (4 Criteria - Smart Match)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ **เวอร์ชันล็อกคอลัมน์ SALE PRICE (ไม่หยิบ PRICE/MT)**
โดยระบบจะสแกนหาและจับคู่จาก 4 หัวข้อหลักให้อัตโนมัติ:
1. **TYPE OF PRODUCT** | 2. **PACKAGING** | 3. **MATERIAL** | 4. **RATIO**
""")

st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

def find_smart_column(df_columns, target_keywords, exclude_keywords=[]):
    for col in df_columns:
        col_clean = str(col).strip().upper().replace(" ", "").replace("_", "").replace("-", "")
        
        # ตรวจสอบตัวยกเว้นก่อน (เช่น ป้องกันการหยิบ PRICE/MT)
        is_excluded = False
        for ex_kw in exclude_keywords:
            if ex_kw in col_clean:
                is_excluded = True
                break
        if is_excluded:
            continue
            
        # ตรวจสอบคำสำคัญที่ต้องการ
        for kw in target_keywords:
            if kw in col_clean:
                return col
    return None

def normalize_series(series):
    def clean_val(val):
        if pd.isna(val):
            return ""
        val_str = str(val).strip()
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        return val_str.upper().replace(" ", "").replace("-", "").replace("_", "").replace(".", "").replace("/", "")
    
    return series.apply(clean_val)

if db_file and curr_file:
    df_db = pd.read_excel(db_file)
    df_curr = pd.read_excel(curr_file)
    
    type_kws = ["TYPEOFPRODUCT", "PRODUCTTYPE", "PRODUCT", "ประเภทสินค้า", "ชนิดสินค้า"]
    pkg_kws = ["PACKAGING", "PKG", "PACKAGE", "บรรจุภัณฑ์", "แพ็คเกจ", "ถุง"]
    mat_kws = ["MATERIAL", "MAT", "GRADE", "วัสดุ", "เกรด"]
    ratio_kws = ["RATIO", "อัตราส่วน", "สัดส่วน", "เปอร์เซ็นต์", "MESH"]
    
    # เจาะจงคำค้นหาสำหรับราคาขาย และตั้งค่าตัวยกเว้นเพื่อหลีกเลี่ยง PRICE/MT
    price_kws = ["SALEPRICE", "ราคาขาย", "PRICE", "ราคา"]
    price_excludes = ["MT", "TON", "PERMT", "ต่อตัน"]

    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_ratio_col = find_smart_column(df_db.columns, ratio_kws)
    
    # ใช้ฟังก์ชันที่เพิ่มตัวยกเว้น คอลัมน์ฝั่ง Database จะไม่หยิบ PRICE/MT แน่นอน
    db_price_col = find_smart_column(df_db.columns, price_kws, exclude_keywords=price_excludes)

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
            st.success("🔍 พบคอลัมน์หลักฝั่ง Database เรียบร้อยแล้ว")
            st.text(f"- ประเภท: {db_type_col}")
            st.text(f"- บรรจุภัณฑ์: {db_pkg_col}")
            st.text(f"- วัสดุ: {db_mat_col}")
            st.text(f"- อัตราส่วน: {db_ratio_col}")
