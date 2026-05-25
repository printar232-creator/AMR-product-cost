import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Product Price Matcher", layout="wide")

st.title("📦 AMR Product Price Matching System")
st.markdown("""
ระบบจับคู่และอัปเดตข้อมูลราคาขาย (**SALE PRICE**) อัตโนมัติ โดยมีเงื่อนไขการตรวจสอบคอลัมน์ตรงกันแบบ 100%:
1. **TYPE OF PRODUCT** (ประเภทสินค้า)
2. **PACKAGING** (บรรจุภัณฑ์)
3. **MATERIAL** (วัสดุ)
""")

# แถบเมนูด้านซ้ายสำหรับอัปโหลดไฟล์
st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลราคา (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

if db_file and curr_file:
    try:
        # อ่านข้อมูลจากไฟล์ Excel เข้าสู่ Pandas DataFrame
        df_db = pd.read_excel(db_file)
        df_curr = pd.read_excel(curr_file)
        
        st.subheader("📊 หน้าต่างตรวจสอบโครงสร้างข้อมูล (Preview)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**ตัวอย่างข้อมูลในฐานข้อมูลต้นทาง (Database):**")
            st.dataframe(df_db.head(5))
        with col2:
            st.markdown("**ตัวอย่างข้อมูลปัจจุบันก่อนเติมราคา (Current Data):**")
            st.dataframe(df_curr.head(5))
            
        # เงื่อนไขคอลัมน์ที่ต้องใช้ในการตรวจสอบ
        matching_criteria = ["TYPE OF PRODUCT", "PACKAGING", "MATERIAL"]
        
        # ตรวจสอบชื่อคอลัมน์ว่าถูกต้องหรือไม่
        if not all(col in df_db.columns for col in matching_criteria) or "SALE PRICE" not in df_db.columns:
            st.error("❌ ข้อผิดพลาด: โครงสร้างไฟล์ฐานข้อมูลไม่ถูกต้อง กรุณาเช็คคำสะกดของหัวคอลัมน์ให้ตรงตามเงื่อนไข")
        elif not all(col in df_curr.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: ไฟล์ข้อมูลปัจจุบันไม่มีคอลัมน์ที่จำเป็นสำหรับการ matching 3 คอลัมน์")
        else:
            if st.button("🚀 เริ่มต้นกระบวนการจับคู่ราคา (Process Matching)"):
                
                # ลบช่องว่างส่วนเกินหน้า-หลังข้อความ (Data Cleaning) เพื่อความแม่นยำสูง
                for df in [df_db, df_curr]:
                    for col in matching_criteria:
                        df[col] = df[col].astype(str).str.strip()
                
                # เคลียร์ข้อมูลซ้ำซ้อนในฐานข้อมูล (ถ้ามี) โดยยึดราคาล่าสุดด้านล่างสุด
                df_db_clean = df_db.drop_duplicates(subset=matching_criteria, keep='last')
                
                # ลบคอลัมน์ SALE PRICE เดิมในไฟล์ปัจจุบันออกก่อน (ถ้ามี) เพื่อไม่ให้เกิดคอลัมน์ซ้ำซ้อนหลังจอยน์
                df_curr_clean = df_curr.drop(columns=["SALE PRICE"], errors="ignore")
                
                # ทำกระบวนการจับคู่ข้ามไฟล์ด้วย Left Join (เหมือนการทำ VLOOKUP/XLOOKUP แบบ 3 เงื่อนไขพร้อมกัน)
                df_result = pd.merge(
                    df_curr_clean,
                    df_db_clean[matching_criteria + ["SALE PRICE"]],
                    on=matching_criteria,
                    how="left"
                )
                
                # หากไม่พบข้อมูล (ค่าเป็น NaN) ให้ระ
