import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AMR Product Pricing Matcher", layout="wide")

st.title("📦 ระบบบันทึกใบส่งสินค้าชั่วคราว & คำนวณราคาขาย (AMR)")
st.write("อัปโหลดไฟล์รายการส่งสินค้าชั่วคราวเพื่อเติมช่อง **SALE PRICE** โดยอัตโนมัติจากฐานข้อมูลราคา")

# 1. ตั้งชื่อไฟล์ฐานข้อมูลที่อยู่ใน GitHub Repository เดียวกัน
DB_FILENAME = "database for product cost AMR.xlsx"

@st.cache_data
def load_database(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        # อ่านไฟล์ Excel 
        df_db = pd.read_excel(file_path)
        # ปรับชื่อคอลัมน์เป็นตัวพิมพ์ใหญ่และตัดช่องว่างเพื่อป้องกันความผิดพลาดในการค้นหา
        df_db.columns = df_db.columns.str.strip().str.upper()
        return df_db
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์ฐานข้อมูล: {e}")
        return None

df_db = load_database(DB_FILENAME)

if df_db is None:
    st.warning(f"⚠️ ไม่พบไฟล์ฐานข้อมูล `{DB_FILENAME}` ในระบบ กรุณาตรวจสอบว่าได้อัปโหลดไฟล์นี้ไว้ใน GitHub Repository เดียวกันแล้ว")
else:
    st.success(f"✅ โหลดฐานข้อมูลสินค้า `{DB_FILENAME}` เรียบร้อยแล้ว")
    
    # แสดงตัวอย่างข้อมูลในฐานข้อมูล (ซ่อนไว้ในแถบเปิด-ปิด)
    with st.expander("ดูข้อมูลฐานข้อมูลราคาต้นทุน/ราคาขาย (Database)"):
        st.dataframe(df_db.head())

st.markdown("---")

# 2. ส่วนสำหรับการอัปโหลดไฟล์ใบส่งสินค้าชั่วคราว
uploaded_file = st.file_uploader("📂 ลากและวาง หรือเลือกไฟล์ใบส่งสินค้าชั่วคราวประจำเดือน (.xlsx, .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # ตรวจสอบชนิดไฟล์และเปิดอ่านข้อมูล
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
            
        st.subheader("📋 ตัวอย่างข้อมูลที่อัปโหลดเข้ามา")
        st.dataframe(df_input.head())
        
        # คัดลอกข้อมูลมาปรับโครงสร้างหัวตารางเป็นตัวพิมพ์ใหญ่เพื่อใช้ประมวลผลภายใน
        df_proc = df_input.copy()
        df_proc.columns = df_proc.columns.str.strip().str.upper()
        
        # ตรวจสอบคอลัมน์สำคัญที่ต้องมีในไฟล์ที่ผู้ใช้อัปโหลดเข้ามา
        required_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]
        missing_cols = [col for col in required_cols if col not in df_proc.columns]
        
        if missing_cols:
            st.error(f"❌ ไม่พบคอลัมน์ที่จำเป็นในไฟล์ที่นำเข้า: {', '.join(missing_cols)} (กรุณาตรวจสอบการสะกดชื่อคอลัมน์ในไฟล์ให้ถูกต้อง)")
        else:
            if st.button("🚀 เริ่มประมวลผลจับคู่ราคา SALE PRICE"):
                with st.spinner("กำลังดึงข้อมูลและแมตช์ราคาขาย..."):
                    
                    # คอลัมน์ที่ต้องใช้รวบรวมจากฝั่ง Database
                    db_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL", "SALE PRICE"]
                    
                    if not all(col in df_db.columns for col in db_cols):
                        st.error("❌ โครงสร้างตารางในไฟล์ฐานข้อมูลกลางไม่ถูกต้อง! ต้องมีคอลัมน์ชื่อ: TYPE OF PRODUCT, PAKAGING, MATERIAL, SALE PRICE")
                    else:
                        # เตรียมข้อมูลฝั่งฐานข้อมูล (ดึงเฉพาะที่จำเป็น และลบรายการซ้ำซ้อนออก)
                        df_db_clean = df_db[db_cols].drop_duplicates(subset=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"])
                        
                        # ล้างค่าช่องว่าง (Trailing spaces) ของตัวอักษรเพื่อไม่ให้เกิดปัญหาแมตช์ไม่เจอจากวรรคเกิน
                        for col in ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]:
                            df_proc[col] = df_proc[col].astype(str).str.strip()
                            df_db_clean[col] = df_db_clean[col].astype(str).str.strip()
                        
                        # ลบคอลัมน์ SALE PRICE เดิมในไฟล์ที่ส่งเข้ามา (ถ้ามีอยู่แล้วแบบว่างๆ) เพื่อป้องกันคอลัมน์ทับซ้อนกัน
                        if "SALE PRICE" in df_proc.columns:
                            df_proc = df_proc.drop(columns=["SALE PRICE"])
                            
                        # ค้นหาและจับคู่ข้อมูลราคาด้วยวิธี Merge (เสมือน VLOOKUP บนเงื่อนไขหลายคอลัมน์)
                        df_result_proc = pd.merge(df_proc, df_db_clean, on=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"], how="left")
                        
                        # สร้างตัวแปรส่งออกแบบคงรูปแบบชื่อคอลัมน์เดิมของผู้ใช้ไว้ และเติมข้อมูลราคาขายที่ดึงได้
                        df_final = df_input.copy()
                        df_final["SALE PRICE"] = df_result_proc["SALE PRICE"]
                        
                        st.subheader("✨ พรีวิวผลลัพธ์ข้อมูลใหม่ที่เติมราคาขายแล้ว")
                        st.dataframe(df_final)
                        
                        # แสดงสถิติการดึงข้อมูล
                        matched_count = df_final["SALE PRICE"].notna().sum()
                        unmatched_count = df_final["SALE PRICE"].isna().sum()
                        st.info(f"📊 สรุปการทำงาน: จับคู่ราคาสำเร็จ {matched_count} รายการ | ⚠️ ไม่พบราคาในฐานข้อมูล {unmatched_count} รายการ")
                        
                        # ฟังก์ชันสำหรับแปลง DataFrame กลับเป็น Excel (.xlsx) เพื่อให้ดาวน์โหลด
                        import io
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_final.to_excel(writer, index=False, sheet_name='Sheet1')
                        excel_data = output.getvalue()
                        
                        # แสดงปุ่มให้ดาวน์โหลดไฟล์ใหม่ที่ผ่านการประมวลผลแล้ว
                        st.download_button(
                            label="📥 ดาวน์โหลดไฟล์ผลลัพธ์ใบส่งสินค้าใหม่ (.xlsx)",
                            data=excel_data,
                            file_name=f"Processed_{
