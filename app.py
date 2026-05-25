import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. ตั้งค่าหน้าตาของโปรแกรมระบบพื้นฐาน
st.set_page_config(
    page_title="AMR Product Cost & Delivery Record System",
    page_icon="📊",
    layout="wide"
)

# 2. แสดงหัวข้อหลักและคำอธิบายด้วยคำสั่งมาตรฐาน
st.title("📊 ระบบคำนวณและเติมช่อง SALE PRICE อัตโนมัติ (AMR)")
st.caption("อัปโหลดไฟล์บันทึกใบส่งสินค้าชั่วคราวประจำเดือน เพื่อเทียบราคาขายจากระบบฐานข้อมูลต้นทุนบน GitHub")

# 3. ตั้งค่าลิงก์ไปยังไฟล์ Database บน GitHub (กรุณาเปลี่ยนลิงก์ให้ตรงกับ Repository ของคุณ)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/database%20for%20product%20cost%20AMR.xlsx"

@st.cache_data
def load_github_database(url):
    """ฟังก์ชันดึงไฟล์เอ็กเซลจากลิงก์ดิบของ GitHub และอ่านแถวที่ 1-92"""
    try:
        # อ่านจากแถวแรก (Row 1) ลงไปจนถึง 92 แถวตามเงื่อนไขข้อมูล
        df_db = pd.read_excel(url, nrows=92)
        
        # ล้างเศษช่องว่างของหัวคอลัมน์
        df_db.columns = df_db.columns.str.strip()
        
        # ปรับข้อมูลคีย์หลักให้เป็นข้อความที่ไม่มีช่องว่างส่วนเกิน
        required_db_cols = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']
        for col in required_db_cols:
            if col in df_db.columns:
                df_db[col] = df_db[col].astype(str).str.strip()
                
        # แปลงราคาขายเป็นรูปแบบตัวเลข
        df_db['SALE PRICE'] = pd.to_numeric(df_db['SALE PRICE'], errors='coerce')
        return df_db, None
    except Exception as e:
        return None, str(e)


# แถบควบคุมด้านข้าง (Sidebar) สำหรับตรวจสอบการเชื่อมต่อข้อมูลหลัก
st.sidebar.header("⚙️ การเชื่อมต่อฐานข้อมูล GitHub")

target_url = st.sidebar.text_input("GitHub Raw URL ของ Database:", GITHUB_RAW_URL)

# เรียกใช้ฟังก์ชันดึงข้อมูลฐานข้อมูลสินค้า
df_db, db_error = load_github_database(target_url)

if db_error:
    st.sidebar.error(f"❌ ไม่สามารถดึงฐานข้อมูลได้: {db_error}")
else:
    st.sidebar.success("✅ โหลดฐานข้อมูลสินค้าเรียบร้อยแล้ว (แถวที่ 1 - 92)")
    if st.sidebar.checkbox("👀 แสดงตัวอย่างตารางอ้างอิง"):
        st.sidebar.dataframe(df_db[['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']].head(15))


# 4. ส่วนรับไฟล์เข้า (File Uploader)
st.subheader("📥 อัปโหลดไฟล์รายการบันทึก / ใบส่งสินค้าชั่วคราว")
uploaded_file = st.file_uploader("เลือกไฟล์เอกสาร Excel ที่ต้องการเติมช่องราคาขาย (SALE PRICE)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # อ่านไฟล์ตารางใบส่งของชั่วคราวที่ผู้ใช้โยนเข้ามาในระบบ
        df_input = pd.read_excel(uploaded_file)
        st.info("🔄 ระบบกำลังประมวลผลการวิเคราะห์และจับคู่ข้อมูล...")
        
        # ล้างเศษเว้นวรรคในชื่อหัวคอลัมน์ของไฟล์ที่อัปโหลดเข้ามา
        df_input.columns = df_input.columns.str.strip()
        
        # เงื่อนไขคีย์หลัก 3 ประการในการ Match ค้นหาราคา
        matching_keys = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL']
        
        # ตรวจสอบโครงสร้างคอลัมน์
        missing_keys = [key for key in matching_keys if key not in df_input.columns]
        if missing_keys:
            st.error(f"❌ โครงสร้างไฟล์ไม่ถูกต้อง: ไม่พบคอลัมน์ -> {', '.join(missing_keys)}")
            st.stop()
            
        # เคลียร์ค่าสตริงเว้นวรรคในคอลัมน์ข้อมูล
        df_process = df_input.copy()
        for key in matching_keys:
            df_process[key] = df_process[key].astype(str).str.strip()
            
        if df_db is not None:
            # ลบคอลัมน์ SALE PRICE เดิมที่มีอยู่ในไฟล์อัปโหลดออกก่อนเพื่อแทนที่ด้วยค่าใหม่
            if 'SALE PRICE' in df_process.columns:
                df_process = df_process.drop(columns=['SALE PRICE'])
                
            # ยุบรวมข้อมูลฐานข้อมูลป้องกันราคาซ้ำซ้อน
            df_db_lookup = df_db[matching_keys + ['SALE PRICE']].drop_duplicates(subset=matching_keys
