import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Product Price Matcher", layout="wide")

st.title("📦 AMR Product Data Matching System (All Rows & Columns)")
st.markdown("""
ระบบจับคู่และดึงข้อมูลสินค้าอัตโนมัติ โดยทำการดึงข้อมูลมา**ครบทุกคอลัมน์ และครบทุก Row จากฐานข้อมูล** อ้างอิงเงื่อนไขการตรวจสอบ:
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
            st.markdown(f"**ตัวอย่างข้อมูลในฐานข้อมูลต้นทาง (Database) - ทั้งหมด {len(df_db)} แถว:**")
            st.dataframe(df_db.head(5))
        with col2:
            st.markdown(f"**ตัวอย่างข้อมูลปัจจุบันก่อนเติม (Current Data) - ทั้งหมด {len(df_curr)} แถว:**")
            st.dataframe(df_curr.head(5))
            
        # เงื่อนไขคอลัมน์ที่ต้องใช้ในการตรวจสอบ
        matching_criteria = ["TYPE OF PRODUCT", "PACKAGING", "MATERIAL"]
        
        # ตรวจสอบชื่อคอลัมน์ว่าถูกต้องหรือไม่
        if not all(col in df_db.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: โครงสร้างไฟล์ฐานข้อมูลไม่ถูกต้อง กรุณาเช็คคำสะกดของหัวคอลัมน์หลัก 3 คอลัมน์")
        elif not all(col in df_curr.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: ไฟล์ข้อมูลปัจจุบันไม่มีคอลัมน์ที่จำเป็นสำหรับการ matching 3 คอลัมน์")
        else:
            if st.button("🚀 เริ่มต้นกระบวนการดึงข้อมูลทุกคอลัมน์และทุกแถว (Process Full Matching)"):
                
                # 1. ลบช่องว่างส่วนเกินหน้า-หลังข้อความ (Data Cleaning) ของคอลัมน์หลักเพื่อความแม่นยำในการ Match
                for df in [df_db, df_curr]:
                    for col in matching_criteria:
                        df[col] = df[col].astype(str).str.strip()
                
                # 2. ค้นหาคอลัมน์ใหม่ๆ จากฐานข้อมูลที่จะนำมาเพิ่ม (ยกเว้นคอลัมน์เงื่อนไขหลัก)
                # และรวมคอลัมน์ยอดฮิตอย่าง SALE PRICE เข้าไปด้วย
                extra_cols_in_db = [col for col in df_db.columns if col not in matching_criteria]
                
                # ลบคอลัมน์เหล่านั้นออกจากไฟล์ปัจจุบันก่อน (ถ้ามีอยู่แล้วแต่เป็นช่องว่าง) เพื่อป้องกันคอลัมน์ซ้ำซ้อนพ่วงท้ายตัวอักษรแปลกๆ
                df_curr_clean = df_curr.drop(columns=[col for col in extra_cols_in_db if col in df_curr.columns], errors="ignore")
                
                # 3. ใช้ Left Join แบบดึงมาทุก Row (ไม่มีการ Drop Duplicates ในฐานข้อมูล) 
                # วิธีนี้จะทำให้ข้อมูลจาก Database ทุกคอลัมน์และทุก Row ที่ตรงเงื่อนไขถูกดึงมาใส่ในโครงสร้างไฟล์ปัจจุบันอย่างครบถ้วน
                df_result = pd.merge(
                    df_curr_clean,
                    df_db,
                    on=matching_criteria,
                    how="left"
                )
                
                # 4. หากช่องไหนจับคู่ไม่เจอ (ค่าเป็น NaN) ให้ใส่ระบุเป็น "Not Found" หรือเครื่องหมาย "-"
                for col in extra_cols_in_db:
                    if col in df_result.columns:
                        df_result[col] = df_result[col].fillna("Not Found")
                
                st.success(f"✅ ดึงข้อมูลทุกช่องและทุก Row จาก Database สำเร็จแล้ว! (รวมผลลัพธ์ทั้งสิ้น {len(df_result)} แถว)")
                
                # แสดงตารางผลลัพธ์ที่อัปเดตข้อมูลครบถ้วนแล้ว
                st.markdown("### 📋 ตารางผลลัพธ์ข้อมูลเวอร์ชันสมบูรณ์")
                st.dataframe(df_result)
                
                # แปลงข้อมูล DataFrame กลับเป็นไฟล์ Excel สำหรับดาวน์โหลด
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_result.to_excel(writer, index=False, sheet_name='Full_Updated_Data')
                processed_data = output.getvalue()
                
                # ปุ่มดาวน์โหลดไฟล์
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ผลลัพธ์เวอร์ชันอัปเดตเต็มรูปแบบ (Excel)",
                    data=processed_data,
                    file_name="amr_full_product_dataset.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดทางเทคนิคระหว่างประมวลผลไฟล์: {e}")
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นระบบงาน")
