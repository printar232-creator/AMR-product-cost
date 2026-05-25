import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (Strict 4-Criteria Reading)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบอ่านเงื่อนไขครบถ้วน
- **ลอจิกการทำงาน:** ระบบจะอ่านและตรวจสอบข้อมูลจากทั้ง 4 คอลัมน์หลักก่อน (`TYPE OF PRODUCT`, `PACKAGING`, `MATERIAL`, `RATIO`) 
- แล้วนำไปเทียบกับฐานข้อมูลต้นทางอย่างแม่นยำ ก่อนจะนำราคาขายมาเติมให้ในช่องสุดท้าย โดยไม่กระทบกับข้อมูลเดิมครับ
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

def normalize_series(series):
    return series.astype(str).str.strip().str.upper()\
                 .str.replace(" ", "", regex=False)\
                 .str.replace("-", "", regex=False)\
                 .str.replace("_", "", regex=False)\
                 .str.replace(".", "", regex=False)\
                 .str.replace("/", "", regex=False)\
                 .replace(["NONE", "NAN", ""], "EMPTY")

if db_file and curr_file:
    df_db = pd.read_excel(db_file)
    df_curr = pd.read_excel(curr_file)
    
    type_kws = ["TYPEOFPRODUCT", "PRODUCTTYPE", "PRODUCT", "ประเภทสินค้า", "ชนิดสินค้า"]
    pkg_kws = ["PACKAGING", "PKG", "PACKAGE", "บรรจุภัณฑ์", "แพ็คเกจ", "ถุง"]
    mat_kws = ["MATERIAL", "MAT", "GRADE", "วัสดุ", "เกรด"]
    ratio_kws = ["RATIO", "อัตราส่วน", "สัดส่วน", "เปอร์เซ็นต์", "MESH"]
    price_kws = ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]

    # 1. ระบบทำการสแกนอ่านคอลัมน์จาก Database ต้นทาง
    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_ratio_col = find_smart_column(df_db.columns, ratio_kws)
    db_price_col = find_smart_column(df_db.columns, price_kws)

    # 2. ระบบทำการสแกนอ่านคอลัมน์จากไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา
    curr_type_col = find_smart_column(df_curr.columns, type_kws)
    curr_pkg_col = find_smart_column(df_curr.columns, pkg_kws)
    curr_mat_col = find_smart_column(df_curr.columns, mat_kws)
    curr_ratio_col = find_smart_column(df_curr.columns, ratio_kws)

    st.subheader("📊 1. ตรวจสอบสถานะการอ่านคอลัมน์ (เงื่อนไข 4 มิติ)")
    
    # ตรวจเช็คความพร้อมของการอ่านข้อมูล
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database) มีทั้งหมด: {len(df_db)} แถว**")
        if db_ready:
            st.success("🔍 ระบบตรวจสอบและอ่านคอลัมน์ฝั่ง Database สำเร็จ")
            st.text(f"- อ่าน TYPE OF PRODUCT จาก: '{db_type_col}'")
            st.text(f"- อ่าน PACKAGING จาก: '{db_pkg_col}'")
            st.text(f"- อ่าน MATERIAL จาก: '{db_mat_col}'")
            st.text(f"- อ่าน RATIO จาก: '{db_ratio_col if db_ratio_col else 'ไม่พบ (จะใช้ระบจับคู่เสมือน)'}'")
            st.text(f"- อ่านดึง SALE PRICE จาก: '{db_price_col}'")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_db)
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา มีทั้งหมด: {len(df_curr)} แถว**")
        if curr_ready:
            st.success("🔍 ระบบตรวจสอบและอ่านคอลัมน์ฝั่ง ไฟล์ปัจจุบัน สำเร็จ")
            st.text(f"- อ่าน TYPE OF PRODUCT จาก: '{curr_type_col}'")
            st.text(f"- อ่าน PACKAGING จาก: '{curr_pkg_col}'")
            st.text(f"- อ่าน MATERIAL จาก: '{curr_mat_col}'")
            st.text(f"- อ่าน RATIO จาก: '{curr_ratio_col if curr_ratio_col else 'ไม่พบ'}'")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_curr)

    if not db_ready or not curr_ready:
        st.warning("⚠️ โปรดตรวจสอบคอลัมน์ของทั้ง 2 ไฟล์ให้มีฟิลด์ข้อมูลให้ครบถ้วนก่อนรันระบบครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มทำการอ่านค่า 4 มิติ และกรอกราคาขาย (Run Match & Populate)"):
            
            db_working = df_db.copy()
            df_final_output = df_curr.copy()
            
            # เคลียร์คอลัมน์ราคาเดิมที่มีอยู่ในไฟล์ปัจจุบันออกก่อน เพื่อรอใส่ค่าใหม่ที่ดึงมา
            cols_to_drop = []
            for c in df_final_output.columns:
                c_upper = str(c).strip().upper().replace(" ", "")
                if c_upper in ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]:
                    cols_to_drop.append(c)
            df_final_output = df_final_output.drop(columns
