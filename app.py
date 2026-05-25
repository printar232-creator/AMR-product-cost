import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System")
st.markdown("ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบอ่านเงื่อนไขครบถ้วน 4 มิติ")

st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบัน", type=["xlsx"])

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

    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_ratio_col = find_smart_column(df_db.columns, ratio_kws)
    db_price_col = find_smart_column(df_db.columns, price_kws)

    curr_type_col = find_smart_column(df_curr.columns, type_kws)
    curr_pkg_col = find_smart_column(df_curr.columns, pkg_kws)
    curr_mat_col = find_smart_column(df_curr.columns, mat_kws)
    curr_ratio_col = find_smart
