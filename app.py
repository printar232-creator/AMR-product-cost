# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. ตั้งค่าหน้าตาของโปรแกรม Streamlit ให้สวยงามและเหมาะสมกับงานข้อมูล
st.set_page_config(
    page_title="AMR Product Cost & Delivery Record System",
    page_icon="📊",
    layout="wide"
)

# สไตล์ลิ่งส่วนหน้าตาเว็บเพิ่มเติม (CSS) เพื่อให้อ่านง่าย ดูเป็นระบบ Professional
st.markdown("""
    <style>
    .main-header { font-family: 'Arial', sans-serif; color: #1E3A8A; font-weight: bold; padding-bottom: 5px; }
    .sub-header { color: #4B5563; font-size: 1.05rem; margin-bottom: 25px; }
    div.stButton > button:first-child {
        background-color: #1E3A8A; color: white; border-radius: 6px; padding: 0.5rem 2rem; font-weight: bold;
    }
    div.stButton > button:first-child:hover { background-color: #2563EB; border-color: #2563EB; }
    </style>
""", unsafe_html=True)

st.markdown('<h1 class="main-header">📊 ระบบคำนวณและเติมช่อง SALE PRICE อัตโนมัติ (AMR)</h1>', unsafe_html=True)
st.markdown('<p class="sub-header">อัปโหลดไฟล์บันทึกใบส่งสินค้าชั่วคราวประจำเดือน เพื่อเทียบราคาขายจากระบบฐานข้อมูลต้นทุนบน GitHub</p>', unsafe_html=True)

# 2. ตั้งค่าลิงก์ไปยังไฟล์ Database บน GitHub 
# !! คำแนะนำ: เปลี่ยนส่วน 'YOUR_GITHUB_USERNAME' และ 'YOUR_REPO_NAME' ให้ตรงกับสิทธิ์การเข้าถึงของคุณบน GitHub
# !! สำคัญ: ลิงก์ต้องเป็นลิงก์แบบดิบ (Raw URL) เพื่อให้สคริปต์เปิดอ่านเนื้อหาตารางได้โดยตรง
GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/database%20for%20product%20cost%20AMR.xlsx"

@st.cache_data
def load_github_database(url):
    """ฟังก์ชันดึงไฟล์เอ็กเซลจากลิงก์ดิบของ GitHub และอ่านแถวที่ 1-92"""
    try:
        # ใช้ nrows=92 เพื่อระบุให้อ่านจากแถวแรก (Row 1) ลงไปจนถึง 92 แถวถัดมาตามเงื่อนไขข้อจำกัดข้อมูล
        df_db = pd.read_excel(url, nrows=92)
        
        # ล้างเศษช่องว่าง (White space) ของหัวคอลัมน์เพื่อความแม่นยำในการแมตช์
        df_db.columns = df_db.columns.str.strip()
        
        # ตรวจสอบคอลัมน์สำคัญที่ต้องดึงมาใช้งาน
        required_db_cols = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']
        for col in required_db_cols:
            if col in df_db.columns:
                df_db[col] = df_db[col].astype(str).str.strip()
                
        # แปลงราคาขายกลับเป็นรูปแบบตัวเลขทศนิยมสำหรับการนำไปคำนวณหรือแสดงผลต่อ
        df_db['SALE PRICE'] = pd.to_numeric(df_db['SALE PRICE'], errors='coerce')
        return df_db, None
    except Exception as e:
        return None, str(e)


# แถบควบคุมด้านข้าง (Sidebar) สำหรับตรวจสอบการเชื่อมต่อข้อมูลหลัก
st.sidebar.header("⚙️ การเชื่อมต่อฐานข้อมูล GitHub")
st.sidebar.info("ระบบจะเรียกดูข้อมูลแบบ Real-time จากไฟล์ `database for product cost AMR.xlsx` ที่เก็บไว้ในคลังโปรเจกต์ของคุณ")

target_url = st.sidebar.text_input("GitHub Raw URL ของ Database:", GITHUB_RAW_URL)

# เรียกใช้ฟังก์ชันดึงข้อมูลฐานข้อมูลสินค้า
df_db, db_error = load_github_database(target_url)

if db_error:
    st.sidebar.error(f"❌ ไม่สามารถดึงฐานข้อมูลจากลิงก์ที่ระบุได้: {db_error}")
    st.sidebar.warning("💡 ข้อแนะนำ: ตรวจสอบว่าคลังข้อมูลของคุณเป็น 'Public' หรือลิงก์ที่ใช้เป็นแบบ Raw แล้วหรือยัง")
else:
    st.sidebar.success("✅ โหลดฐานข้อมูลสินค้าเรียบร้อยแล้ว (แถวที่ 1 - 92)")
    if st.sidebar.checkbox("👀 แสดงตัวอย่างตารางข้อมูลอ้างอิง"):
        st.sidebar.dataframe(df_db[['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']].head(15))


# 3. ส่วนรับไฟล์เข้า (File Uploader สำหรับผู้ใช้งานหน้าร้านหรือหน้าโรงงาน)
st.subheader("📥 อัปโหลดไฟล์รายการบันทึก / ใบส่งสินค้าชั่วคราว")
uploaded_file = st.file_uploader("เลือกไฟล์เอกสาร Excel ที่ต้องการเติมช่องราคาขาย (SALE PRICE)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # อ่านไฟล์ตารางใบส่งของชั่วคราวที่โยนเข้าในระบบ
        df_input = pd.read_excel(uploaded_file)
        
        st.info("🔄 ระบบกำลังประมวลผลการวิเคราะห์และตรวจสอบโครงสร้างเงื่อนไขสินค้า...")
        
        # ล้างเศษเว้นวรรคในชื่อหัวคอลัมน์ของไฟล์ที่อัปโหลดเข้ามา
        df_input.columns = df_input.columns.str.strip()
        
        # เงื่อนไขคีย์หลัก 3 ประการในการ Match ค้นหาราคา
        matching_keys = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL']
        
        # ตรวจสอบว่าโครงสร้างคอลัมน์ในไฟล์ครบถ้วนตามความต้องการหรือไม่
        missing_keys = [key for key in matching_keys if key not in df_input.columns]
        if missing_keys:
            st.error(f"❌ โครงสร้างไฟล์ไม่ถูกต้อง: ไม่พบคอลัมน์ต่อไปนี้ในไฟล์ที่อัปโหลด -> {', '.join(missing_keys)}")
            st.stop()
            
        # เคลียร์ค่าสตริงเว้นวรรคในคอลัมน์ข้อมูลเพื่อให้ระบบข้อความตรงกันเป๊ะๆ (Case-insensitive & Space-insensitive)
        df_process = df_input.copy()
        for key in matching_keys:
            df_process[key] = df_process[key].astype(str).str.strip()
            
        if df_db is not None:
            # หากไฟล์ที่ส่งมามีคอลัมน์ 'SALE PRICE' อยู่แล้ว (แต่เป็นช่องว่างหรือข้อมูลเก่า) 
            # ลบคอลัมน์นั้นทิ้งชั่วคราว เพื่อนำค่าที่อัปเดตล่าสุดจากฐานข้อมูลใส่เข้าไปแทนที่
            if 'SALE PRICE' in df_process.columns:
                df_process = df_process.drop(columns=['SALE PRICE'])
                
            # กรองและยุบรวมข้อมูลฐานข้อมูลให้เหลือแต่ Key และ Value ราคาขายที่สะอาด ป้องกันราคาซ้ำซ้อน
            df_db_lookup = df_db[matching_keys + ['SALE PRICE']].drop_duplicates(subset=matching_keys)
            
            # ดำเนินการเปรียบเทียบตารางแบบเงื่อนไขกลุ่ม (Multi-column VLOOKUP ด้วยกระบวนการ Left Merge ใน pandas)
            df_result = pd.merge(
                df_process,
                df_db_lookup,
                on=matching_keys,
                how='left'
            )
            
            # ตรวจสอบข้อมูลสถิติที่ทำการแมตช์ได้สำเร็จ
            matched_rows = df_result['SALE PRICE'].notna().sum()
            unmatched_rows = df_result['SALE PRICE'].isna().sum()
            
            # แสดงบอร์ดสรุปสถานะสั้นๆ (Metrics Dashboard)
            st.success("🎉 ประมวลผลและอัปเดตราคาเสร็จสิ้น!")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("จำนวนรายการทั้งหมดที่พบในไฟล์", f"{len(df_result)} แถว")
            m_col2.metric("เติมราคาสำเร็จ (Matched)", f"{matched_rows} แถว", delta=f"{(matched_rows/len(df_result))*100:.1f}%")
            m_col3.metric("ไม่พบรหัสราคาขายในคลัง", f"{unmatched_rows} แถว", delta=f"-{unmatched_rows}" if unmatched_rows > 0 else "0", delta_color="inverse")
            
            # กรณีที่ข้อมูลบางแถวพิมพ์สเปลลิ่งหรือประเภทไม่ตรงกับ Database จะแสดงข้อความเตือนให้ผู้ใช้ทราบ
            if unmatched_rows > 0:
                st.warning("⚠️ พบปัญหา: มีบางรายการไม่พบราคาขายเนื่องจากข้อมูลผลิตภัณฑ์ บรรจุภัณฑ์ หรือประเภทวัสดุไม่มีอยู่ในแถว 1-92 ของฐานข้อมูลต้นทาง")
            
            # 4. แสดงพรีวิวผลลัพธ์ของไฟล์ใหม่ที่มีการเติมช่องราคาแล้ว
            st.subheader("📋 ตัวอย่างตารางข้อมูลของไฟล์ใหม่ (ข้อมูลอัปเดตช่อง SALE PRICE)")
            st.dataframe(df_result)
            
            # 5. แปลงข้อมูลลงสู่หน่วยความจำ (Buffer IO) เพื่อเขียนไฟล์ Excel ตัวใหม่ออกมาโดยไม่ต้องบันทึกลงดิสก์ระบบ
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Monthly_Sale_Prices')
                
            # สร้างปุ่มสำหรับดาวน์โหลดไฟล์ผลลัพธ์ใหม่กลับไปยังคอมพิวเตอร์ของผู้ใช้
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel (เวอร์ชันเติมราคา SALE PRICE แล้ว)",
                data=excel_buffer.getvalue(),
                file_name="รายการบันทึกใบส่งสินค้า_อัปเดตราคาขายประจำเดือน.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as err:
        st.error(f"🚨 ระบบตรวจพบข้อผิดพลาดขณะเขียนหรือแปลงข้อมูล: {str(err)}")
