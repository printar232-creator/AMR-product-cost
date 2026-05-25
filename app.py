import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Product Price Matcher", layout="wide")

st.title("📦 AMR Product Data Matching System (Full Columns)")
st.markdown("""
ระบบจับคู่และอัปเดตข้อมูลสินค้าอัตโนมัติ โดยทำการดึงข้อมูลมา**ครบทุกคอลัมน์**จากไฟล์ฐานข้อมูล อ้างอิงเงื่อนไขการตรวจสอบ:
1. **TYPE OF PRODUCT** (ประเภทสินค้า)
2. **PACKAGING** (บรรจุภัณฑ์)
3. **MATERIAL** (วัสดุ)
""")

# แถบเมนูด้านซ้ายสำหรับอัปโหลดไฟล์
st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมข้อมูลให้ครบ", type=["xlsx"])

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
            st.markdown("**ตัวอย่างข้อมูลปัจจุบันก่อนเติม (Current Data):**")
            st.dataframe(df_curr.head(5))
            
        # เงื่อนไขคอลัมน์ที่ต้องใช้ในการตรวจสอบ
        matching_criteria = ["TYPE OF PRODUCT", "PACKAGING", "MATERIAL"]
        
        # ตรวจสอบชื่อคอลัมน์ว่าถูกต้องหรือไม่
        if not all(col in df_db.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: โครงสร้างไฟล์ฐานข้อมูลไม่ถูกต้อง กรุณาเช็คคำสะกดของหัวคอลัมน์หลัก 3 คอลัมน์")
        elif not all(col in df_curr.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: ไฟล์ข้อมูลปัจจุบันไม่มีคอลัมน์ที่จำเป็นสำหรับการ matching 3 คอลัมน์")
        else:
            if st.button("🚀 เริ่มต้นกระบวนการดึงข้อมูลทุกคอลัมน์ (Process Matching)"):
                
                # 1. ลบช่องว่างส่วนเกินหน้า-หลังข้อความ (Data Cleaning) ของคอลัมน์หลักเพื่อความแม่นยำ
                for df in [df_db, df_curr]:
                    for col in matching_criteria:
                        df[col] = df[col].astype(str).str.strip()
                
                # 2. หาคอลัมน์ทั้งหมดจากฐานข้อมูลที่ต้องการดึงมา (ยกเว้นกรณีคอลัมน์ซ้ำซ้อนกับไฟล์ปัจจุบัน)
                # วิธีนี้จะทำให้ดึงมาครบทุกช่อง ไม่ว่าใน database จะมีกี่คอลัมน์ก็ตาม เช่น SG, Mesh, Cost, Price
                cols_to_keep = matching_criteria + [col for col in df_db.columns if col not in df_curr.columns or col == "SALE PRICE"]
                
                # เคลียร์ข้อมูลซ้ำซ้อนในฐานข้อมูล (ถ้ามี) โดยยึดข้อมูลแถวล่าสุด
                df_db_clean = df_db.drop_duplicates(subset=matching_criteria, keep='last')[cols_to_keep]
                
                # ลบคอลัมน์ที่ซ้ำซ้อนออกจากไฟล์ปัจจุบันก่อนทำการจับคู่ (เพื่อป้องกันคอลัมน์งอกเป็น _x, _y)
                extra_cols = [col for col in df_db.columns if col in df_curr.columns and col not in matching_criteria]
                df_curr_clean = df_curr.drop(columns=extra_cols, errors="ignore")
                
                # 3. ทำกระบวนการจับคู่ข้ามไฟล์ด้วย Left Join เพื่อดึงทุกคอลัมน์มาพร้อมกัน
                df_result = pd.merge(
                    df_curr_clean,
                    df_db_clean,
                    on=matching_criteria,
                    how="left"
                )
                
                # 4. หากช่องไหนไม่พบข้อมูล (ค่าเป็น NaN) ให้ระบุเป็น "Not Found" หรือ "-" 
                # ดำเนินการเฉพาะคอลัมน์ที่ดึงมาใหม่
                new_fetched_cols = [col for col in df_result.columns if col not in df_curr_clean.columns or col in extra_cols]
                for col in new_fetched_cols:
                    df_result[col] = df_result[col].fillna("Not Found")
                
                st.success("✅ ดึงข้อมูลทุกช่องจาก Database มาเติมในไฟล์ปัจจุบันสำเร็จแล้ว!")
                
                # แสดงตารางผลลัพธ์ที่อัปเดตข้อมูลครบถ้วนแล้ว
                st.markdown("### 📋 ตารางผลลัพธ์ข้อมูลที่ดึงมาครบทุกคอลัมน์")
                st.dataframe(df_result)
                
                # แปลงข้อมูล DataFrame กลับเป็นไฟล์ Excel สำหรับดาวน์โหลด
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_result.to_excel(writer, index=False, sheet_name='Updated_Data')
                processed_data = output.getvalue()
                
                # ปุ่มดาวน์โหลดไฟล์
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ผลลัพธ์เวอร์ชันอัปเดตครบทุกช่อง (Excel)",
                    data=processed_data,
                    file_name="updated_full_product_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดทางเทคนิคระหว่างประมวลผลไฟล์: {e}")
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นระบบงาน")
