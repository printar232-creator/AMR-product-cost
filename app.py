import streamlit as pd
import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="AMR Sales Price Matcher", layout="wide")

st.title("📦 ระบบบันทึกใบส่งสินค้าชั่วคราวและคำนวณราคาขาย")
st.subheader("บริษัท Asian Mineral Resources (AMR)")

# --- ส่วนการดึงข้อมูล Database จาก GitHub ---
# เปลี่ยน URL ด้านล่างนี้ให้เป็นลิงก์ของ Repository คุณ (ต้องเป็น Raw URL)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/database%20for%20product%20cost%20AMR.xlsx"

@st.cache_data
def load_github_database(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # อ่านไฟล์ Excel ดึงข้อมูลแถว 1 ถึง 92 (index 0 ถึง 91) ทุกคอลัมน์
            df_db = pd.read_excel(BytesIO(response.content))
            df_db = df_db.iloc[0:92]  # จำกัดแถวที่ 1 ถึง 92 ตามเงื่อนไข
            
            # ลบช่องว่างในชื่อคอลัมน์และข้อมูลเพื่อป้องกันการจับคู่พลาด
            for col in ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL']:
                if col in df_db.columns:
                    df_db[col] = df_db[col].astype(str).str.strip()
            return df_db
        else:
            st.error(f"ไม่สามารถดึงไฟล์จาก GitHub ได้ (Status Code: {response.status_code})")
            return None
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลด Database: {e}")
        return None

# โหลดฐานข้อมูลหลัก
df_database = load_github_database(GITHUB_RAW_URL)

if df_database is not None:
    st.success("✅ เชื่อมต่อฐานข้อมูลสินค้าจาก GitHub สำเร็จ (โหลดข้อมูลแล้ว 92 แถว)")
    
    # ดูข้อมูลสแนปชอตของ Database (ซ่อน/แสดงได้)
    with st.expander("🔍 ดูฐานข้อมูลสินค้าอ้างอิง (Database)"):
        st.dataframe(df_database)
        
    # --- ส่วนการอัปโหลดไฟล์ใบส่งสินค้าชั่วคราว ---
    st.markdown("---")
    st.header("📥 อัปโหลดไฟล์ใบส่งสินค้าชั่วคราว (Delivery Order)")
    
    uploaded_file = st.file_uploader("เลือกไฟล์ Excel ของแต่ละเดือนที่ต้องการประมveledผล", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # อ่านไฟล์ที่ผู้ใช้อัปโหลด
            df_user = pd.read_excel(uploaded_file)
            
            # ตรวจสอบคอลัมน์ที่จำเป็นสำหรับการตรวจสอบ
            required_cols = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL']
            missing_cols = [col for col in required_cols if col not in df_user.columns]
            
            if missing_cols:
                st.error(f"❌ ไฟล์ที่อัปโหลดไม่มีคอลัมน์ต่อไปนี้: {', '.join(missing_cols)}")
            else:
                st.info("กำลังประมวลผลคำนวณ SALE PRICE...")
                
                # จัดการข้อมูลฝั่งผู้ใช้ให้ไม่มีช่องว่างส่วนเกิน
                for col in required_cols:
                    df_user[col] = df_user[col].astype(str).str.strip()
                
                # ตรวจสอบว่าใน Database มีคอลัมน์ 'SALE PRICE' หรือไม่
                if 'SALE PRICE' not in df_database.columns:
                    st.error("❌ ไม่พบคอลัมน์ 'SALE PRICE' ในไฟล์ Database บน GitHub")
                else:
                    # เตรียมคอลัมน์สำหรับการ Mapping (เลือกเฉพาะ Key และ Target)
                    df_db_mapping = df_database[['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']].drop_duplicates()
                    
                    # ถ้าไฟล์เดิมของผู้ใช้มีคอลัมน์ SALE PRICE อยู่แล้ว ให้ลบออกก่อนเพื่อใส่ค่าที่อัพเดทใหม่เข้าไป
                    if 'SALE PRICE
