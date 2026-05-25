import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ 
โดยระบบจะสแกนหาและจับคู่จาก 3 หัวข้อหลักที่ชื่อตรงกันให้อัตโนมัติ:
1. **TYPE OF PRODUCT** | 2. **PACKAGING** | 3. **MATERIAL**
""")

# แถบเมนูด้านซ้ายสำหรับอัปโหลดไฟล์
st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

if db_file and curr_file:
    try:
        # อ่านข้อมูลจากไฟล์ Excel
        df_db = pd.read_excel(db_file)
        df_curr = pd.read_excel(curr_file)
        
        # ปรับแต่งหัวคอลัมน์ให้เป็นตัวพิมพ์ใหญ่และตัดช่องว่าง
        def standardize_columns(df):
            df.columns = [str(col).strip().upper() for col in df.columns]
            return df

        df_db = standardize_columns(df_db)
        df_curr = standardize_columns(df_curr)
        
        # คอลัมน์เงื่อนไขหลัก
        required_keys = ["TYPE OF PRODUCT", "PACKAGING", "MATERIAL"]
        
        st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database): {len(df_db)} แถว**")
            st.dataframe(df_db.head(5))
        with col2:
            st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา: {len(df_curr)} แถว**")
            st.dataframe(df_curr.head(5))

        # ตรวจสอบคอลัมน์ในไฟล์
        missing_db = [col for col in required_keys if col not in df_db.columns]
        missing_curr = [col for col in required_keys if col not in df_curr.columns]
        
        if missing_db:
            st.error(f"❌ ไม่พบหัวข้อ {missing_db} ในไฟล์ฐานข้อมูล")
        elif missing_curr:
            st.error(f"❌ ไม่พบหัวข้อ {missing_curr} ในไฟล์ปัจจุบัน")
        elif "SALE PRICE" not in df_db.columns:
            st.error("❌ ไม่พบหัวข้อ 'SALE PRICE' ในไฟล์ฐานข้อมูล (Database)")
        else:
            st.markdown("---")
            if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Auto-Match)"):
                
                # ลบช่องว่างส่วนเกินในข้อมูลของคอลัมน์หลัก
                for col in required_keys:
                    df_db[col] = df_db[col].astype(str).str.strip()
                    df_curr[col] = df_curr[col].astype(str).str.strip()
                
                # เตรียมข้อมูลราคาจากฐานข้อมูลและลบแถวซ้ำ
                df_db_prices = df_db[required_keys + ["SALE PRICE"]].drop_duplicates(subset=required_keys, keep='last')
                
                # ลบคอลัมน์ SALE PRICE เดิมในไฟล์ปัจจุบันออกก่อนเพื่อใส่ราคาใหม่
                df_curr_clean = df_curr.drop(columns=["SALE PRICE"], errors="ignore")
                
                # ทำการจับคู่ข้อมูลแบบ
