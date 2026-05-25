import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Product Data Linker", layout="wide")

st.title("📦 AMR Product Data Matching System (All Database Rows)")
st.markdown("""
ระบบดึงข้อมูลสินค้าอัตโนมัติ โดยทำการกวาดข้อมูล**ทุกแถว (All Rows) และทุกคอลัมน์** จากไฟล์ฐานข้อมูลต้นทางมาแสดงผลทั้งหมด
อ้างอิงเงื่อนไขการตรวจสอบจาก 3 คอลัมน์หลัก:
1. **TYPE OF PRODUCT** (ประเภทสินค้า)
2. **PACKAGING** (บรรจุภัณฑ์)
3. **MATERIAL** (วัสดุ)
""")

# แถบเมนูด้านซ้ายสำหรับอัปโหลดไฟล์
st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการนำมาจับคู่", type=["xlsx"])

if db_file and curr_file:
    try:
        # อ่านข้อมูลจากไฟล์ Excel เข้าสู่ Pandas DataFrame
        df_db = pd.read_excel(db_file)
        df_curr = pd.read_excel(curr_file)
        
        st.subheader("📊 หน้าต่างตรวจสอบข้อมูลต้นฉบับ")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"🗃️ **ไฟล์ฐานข้อมูลต้นทาง (Database) มีทั้งหมด: {len(df_db)} แถว**")
            # แสดงข้อมูลทั้งหมดของ Database โดยไม่มีการใช้ .head() เพื่อให้เห็นครบทุกแถวในโปรแกรม
            st.dataframe(df_db)
        with col2:
            st.markdown(f"📄 **ไฟล์ข้อมูลปัจจุบัน มีทั้งหมด: {len(df_curr)} แถว**")
            st.dataframe(df_curr)
            
        # เงื่อนไขคอลัมน์ที่ต้องใช้ในการตรวจสอบ
        matching_criteria = ["TYPE OF PRODUCT", "PACKAGING", "MATERIAL"]
        
        # ตรวจสอบชื่อคอลัมน์ว่าถูกต้องหรือไม่
        if not all(col in df_db.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: โครงสร้างไฟล์ฐานข้อมูลไม่ถูกต้อง กรุณาเช็คคำสะกดของหัวคอลัมน์หลัก 3 คอลัมน์")
        elif not all(col in df_curr.columns for col in matching_criteria):
            st.error("❌ ข้อผิดพลาด: ไฟล์ข้อมูลปัจจุบันไม่มีคอลัมน์ที่จำเป็นสำหรับการ matching 3 คอลัมน์")
        else:
            if st.button("🚀 เริ่มต้นดึงข้อมูลทุกแถวจาก Database (Process All Rows)"):
                
                # 1. ลบช่องว่างส่วนเกินหน้า-หลังข้อความ (Data Cleaning) เพื่อให้จับคู่ได้แม่นยำ 100%
                for df in [df_db, df_curr]:
                    for col in matching_criteria:
                        df[col] = df[col].astype(str).str.strip()
                
                # 2. หาคอลัมน์ที่มีเฉพาะในไฟล์ปัจจุบัน (เช่น PRODUCT ID หรือรหัสภายในอื่นๆ) 
                # เพื่อนำไปจับคู่กับฐานข้อมูลโดยไม่ให้คอลัมน์ราคาหรือข้อมูลอื่นของเดิมมาขวาง
                extra_cols_in_db = [col for col in df_db.columns if col not in matching_criteria]
                df_curr_clean = df_curr.drop(columns=[col for col in extra_cols_in_db if col in df_curr.columns], errors="ignore")
                
                # 3. เปลี่ยนสิทธิ์การ Join เป็นแบบ 'right' หรือ 'outer' เพื่อให้ "ยึดฝั่งฐานข้อมูลเป็นหลัก" 
                # ข้อมูลทุก row ใน database จะถูกดึงมาครบถ้วน ไม่ว่าจะแมตช์กับไฟล์ปัจจุบันเจอหรือไม่ก็ตาม
                df_result = pd.merge(
                    df_curr_clean,
                    df_db,
                    on=matching_criteria,
                    how="right"  # มั่นใจได้ว่าข้อมูลฝั่ง Database (ขวา) จะมาครบทุก Row แน่นอน
                )
                
                # จัดเรียงคอลัมน์ใหม่ให้สวยงาม (เอาคอลัมน์เงื่อนไขหลักไว้ข้างหน้า)
                all_cols = matching_criteria + [col for col in df_result.columns if col not in matching_criteria]
                df_result = df_result[all_cols]
                
                # 4. เติมคำว่า "Not Found" หรือ "-" ในช่องของคอลัมน์ฝั่งไฟล์ปัจจุบันที่จับคู่กับฐานข้อมูลไม่เจอ
                for col in df_result.columns:
                    df_result[col] = df_result[col].fillna("-")
                
                st.success(f"✅ ดึงข้อมูลสำเร็จ! รวมแถวจากฐานข้อมูลต้นทางออกมาแสดงผลทั้งหมด {len(df_result)} แถว")
                
                # แสดงตารางผลลัพธ์ข้อมูลที่ดึงมาครบทุก row จาก database
                st.markdown("### 📋 ตารางผลลัพธ์รวมข้อมูลทุกแถวจาก Database")
                st.dataframe(df_result)
                
                # แปลงข้อมูล DataFrame กลับเป็นไฟล์ Excel สำหรับดาวน์โหลด
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_result.to_excel(writer, index=False, sheet_name='All_Database_Rows')
                processed_data = output.getvalue()
                
                # ปุ่มดาวน์โหลดไฟล์
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ผลลัพธ์เวอร์ชันกวาดทุกแถว (Excel)",
                    data=processed_data,
                    file_name="amr_all_rows_database.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดทางเทคนิคระหว่างประมวลผลไฟล์: {e}")
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นระบบงาน")
