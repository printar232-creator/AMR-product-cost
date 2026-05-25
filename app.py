import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AMR Product Pricing Matcher", layout="wide")

st.title("📦 ระบบบันทึกใบส่งสินค้าชั่วคราว & คำนวณราคาขาย (AMR)")
st.write("อัปโหลดไฟล์รายการส่งสินค้าชั่วคราวเพื่อเติมช่อง **SALE PRICE** โดยอัตโนมัติจากฐานข้อมูลราคา")

# 1. Database Loading Section (ดึงข้อมูลแถว 1 ถึง 92)
DB_FILENAME = "database for product cost AMR.xlsx"

@st.cache_data
def load_database(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        # ดึงข้อมูลจากแถวที่ 1 ถึง 92 (nrows=91 ไม่รวม Header หรือใช้ 92 ควบคุมขอบเขต)
        # ใน pandas แถวแรกสุดจะถูกใช้เป็น Header อัตโนมัติ และจะอ่านแถวข้อมูลถัดไปอีก 91 แถว รวมเป็น 92 แถวใน Excel
        df_db = pd.read_excel(file_path, nrows=91)
        
        # จัดการล้างหัวตาราง ตัดช่องว่าง และแปลงเป็นตัวพิมพ์ใหญ่
        df_db.columns = df_db.columns.str.strip().str.upper()
        return df_db
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

df_db = load_database(DB_FILENAME)

if df_db is None:
    st.warning(f"⚠️ ไม่พบไฟล์ฐานข้อมูล {DB_FILENAME} ในระบบ กรุณาตรวจสอบการอัปโหลด")
else:
    st.success(f"✅ โหลดฐานข้อมูลสินค้า {DB_FILENAME} (แถว 1 ถึง 92) เรียบร้อยแล้ว")
    with st.expander("ดูข้อมูลฐานข้อมูลราคาต้นทุน/ราคาขาย (Database Preview)"):
        st.dataframe(df_db)

st.markdown("---")

# 2. File Upload & Processing Section
uploaded_file = st.file_uploader("📂 ลากและวาง หรือเลือกไฟล์ใบส่งสินค้าชั่วคราวประจำเดือน (.xlsx, .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
            
        st.subheader("📋 ตัวอย่างข้อมูลที่อัปโหลดเข้ามา")
        st.dataframe(df_input.head())
        
        df_proc = df_input.copy()
        df_proc.columns = df_proc.columns.str.strip().str.upper()
        
        required_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]
        missing_cols = [col for col in required_cols if col not in df_proc.columns]
        
        if missing_cols:
            st.error(f"❌ ไม่พบคอลัมน์ที่จำเป็นในไฟล์ที่นำเข้า: {', '.join(missing_cols)}")
        else:
            if st.button("🚀 เริ่มประมวลผลจับคู่ราคา SALE PRICE"):
                with st.spinner("กำลังประมวลผล..."):
                    db_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL", "SALE PRICE"]
                    
                    if not all(col in df_db.columns for col in db_cols):
                        st.error("❌ โครงสร้างตารางในไฟล์ฐานข้อมูลกลางไม่ถูกต้อง (ต้องมีคอลัมน์ TYPE OF PRODUCT, PAKAGING, MATERIAL, SALE PRICE)")
                    else:
                        # เลือกเฉพาะคอลัมน์ที่จำเป็นและตัดข้อมูลซ้ำซ้อนจากฐานข้อมูลแถว 1-92
                        df_db_clean = df_db[db_cols].drop_duplicates(subset=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"])
                        
                        # ล้างค่าช่องว่างของข้อความเพื่อป้องกันปัญหาการ Match ตัวอักษร
                        for col in ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]:
                            df_proc[col] = df_proc[col].astype(str).str.strip()
                            df_db_clean[col] = df_db_clean[col].astype(str).str.strip()
                        
                        # ลบคอลัมน์ SALE PRICE เดิมในไฟล์ที่ผู้ใช้อัปโหลดมา (ถ้ามี) ออกก่อน เพื่อเติมราคาใหม่
                        if "SALE PRICE" in df_proc.columns:
                            df_proc = df_proc.drop(columns=["SALE PRICE"])
                            
                        # ทำการดึงราคามาใส่ตามเงื่อนไขทั้ง 3 คอลัมน์
                        df_result_proc = pd.merge(df_proc, df_db_clean, on=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"], how="left")
                        
                        # นำผลลัพธ์ใส่กลับโครงสร้างไฟล์เดิมของผู้ใช้
                        df_final = df_input.copy()
                        df_final["SALE PRICE"] = df_
