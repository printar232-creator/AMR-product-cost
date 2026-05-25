import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าตาของโปรแกรม Streamlit
st.set_page_config(page_title="AMR Flexible Data Matcher", layout="wide")

st.title("📦 AMR Product Data Matching System (Fixed Unnamed Columns)")
st.markdown("""
ระบบดึงข้อมูลสินค้าอัจฉริยะ **เวอร์ชันแก้ไขปัญหาคอลัมน์ว่าง/คอลัมน์ซ้ำ (Unnamed Error Fixed)** คุณสามารถเลือกจับคู่คอลัมน์ระหว่าง *ไฟล์ปัจจุบัน* และ *ไฟล์ฐานข้อมูล (Database)* ได้ด้วยตนเองผ่านเมนูด้านล่าง
""")

# แถบเมนูด้านซ้ายสำหรับอัปโหลดไฟล์
st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการนำมาเติมข้อมูล", type=["xlsx"])

if db_file and curr_file:
    try:
        # 1. อ่านข้อมูลจากไฟล์ Excel
        df_db = pd.read_excel(db_file)
        df_curr = pd.read_excel(curr_file)
        
        # ฟังก์ชันพิเศษ: จัดการลบหรือเปลี่ยนชื่อคอลัมน์ที่ซ้ำ/คอลัมน์ว่าง (เช่น Unnamed) เพื่อป้องกัน Error
        def clean_dataframe_columns(df):
            # ลบคอลัมน์ที่เป็นค่าว่างทั้งหมดออกไปก่อน (คอลัมน์ที่ชื่อขึ้นต้นด้วย Unnamed และไม่มีข้อมูล)
            cols_to_drop = [col for col in df.columns if str(col).startswith('Unnamed:') and df[col].isna().all()]
            df = df.drop(columns=cols_to_drop, errors='ignore')
            
            # ถ้ายังมีคอลัมน์ชื่อซ้ำกันอยู่ (รวมถึง Unnamed ที่อาจมีข้อมูลเหลืออยู่) จะทำการรันตัวเลขต่อท้ายให้ชื่อไม่ซ้ำกัน
            new_cols = []
            counts = {}
            for col in df.columns:
                col_str = str(col)
                if col_str in counts:
                    counts[col_str] += 1
                    new_cols.append(f"{col_str}_{counts[col_str]}")
                else:
                    counts[col_str] = 0
                    new_cols.append(col_str)
            df.columns = new_cols
            return df

        # ทำความสะอาดหัวคอลัมน์ของทั้งสองไฟล์ก่อนนำไปแสดงผลและประมวลผล
        df_db = clean_dataframe_columns(df_db)
        df_curr = clean_dataframe_columns(df_curr)
        
        st.subheader("📊 1. ตรวจสอบข้อมูลต้นฉบับ (หลังเคลียร์คอลัมน์ว่าง)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"🗃️ **ไฟล์ฐานข้อมูลต้นทาง (Database): {len(df_db)} แถว**")
            st.dataframe(df_db.head(10))
        with col2:
            st.markdown(f"📄 **ไฟล์ข้อมูลปัจจุบันที่ต้องการกรอก: {len(df_curr)} แถว**")
            st.dataframe(df_curr.head(10))
            
        st.markdown("---")
        st.subheader("🛠️ 2. จับคู่คอลัมน์ที่ต้องการใช้เทียบข้อมูล (Column Mapping)")
        st.info("💡 โปรดเลือกหัวคอลัมน์จากทั้ง 2 ไฟล์ให้สอดคล้องกันเพื่อใช้ในการเทียบจับคู่สินค้า")
        
        # ส่วนการเลือกคอลัมน์อย่างอิสระ
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("### 🔹 เงื่อนไขที่ 1: ประเภทสินค้า")
            db_col_1 = st.selectbox("เลือกคอลัมน์ประเภทสินค้า (ฝั่ง Database)", df_db.columns, key="db1")
            curr_col_1 = st.selectbox("เลือกคอลัมน์ประเภทสินค้า (ฝั่ง ไฟล์ปัจจุบัน)", df_curr.columns, key="curr1")
            
        with c2:
            st.markdown("### 🔹 เงื่อนไขที่ 2: บรรจุภัณฑ์")
            db_col_2 = st.selectbox("เลือกคอลัมน์บรรจุภัณฑ์ (ฝั่ง Database)", df_db.columns, key="db2")
            curr_col_2 = st.selectbox("เลือกคอลัมน์บรรจุภัณฑ์ (ฝั่ง ไฟล์ปัจจุบัน)", df_curr.columns, key="curr2")
            
        with c3:
            st.markdown("### 🔹 เงื่อนไขที่ 3: วัสดุ / เกรด")
            db_col_3 = st.selectbox("เลือกคอลัมน์วัสดุ (ฝั่ง Database)", df_db.columns, key="db3")
            curr_col_3 = st.selectbox("เลือกคอลัมน์วัสดุ (ฝั่ง ไฟล์ปัจจุบัน)", df_curr.columns, key="curr3")

        # ปุ่มเริ่มทำงาน
        if st.button("🚀 เริ่มต้นดึงข้อมูลตามโครงสร้างที่เลือก (Process Matching)"):
            
            db_working = df_db.copy()
            curr_working = df_curr.copy()
            
            # แปลงข้อมูลในคอลัมน์ที่เลือกให้เป็น String และตัดเว้นวรรค
            db_working[db_col_1] = db_working[db_col_1].astype(str).str.strip()
            db_working[db_col_2] = db_working[db_col_2].astype(str).str.strip()
            db_working[db_col_3] = db_working[db_col_3].astype(str).str.strip()
            
            curr_working[curr_col_1] = curr_working[curr_col_1].astype(str).str.strip()
            curr_working[curr_col_2] = curr_working[curr_col_2].astype(str).str.strip()
            curr_working[curr_col_3] = curr_working[curr_col_3].astype(str).str.strip()
            
            # เปลี่ยนชื่อคอลัมน์เปรียบเทียบในฝั่ง Database ให้ชั่วคราวเพื่อให้ชื่อตรงกับไฟล์ปัจจุบันตอนทำ Merge
            rename_dict = {
                db_col_1: curr_col_1,
                db_col_2: curr_col_2,
                db_col_3: curr_col_3
            }
            db_working = db_working.rename(columns=rename_dict)
            
            # คอลัมน์ที่เป็นคีย์ในการ Merge ร่วมกัน
            join_keys = [curr_col_1, curr_col_2, curr_col_3]
            
            # หาคอลัมน์อื่นๆ ที่เหลือทั้งหมดในฐานข้อมูลเพื่อดึงมาให้ครบถ้วน
            extra_db_cols = [col for col in db_working.columns if col not in join_keys]
            
            # ลบคอลัมน์เสริมเหล่านั้นออกจากไฟล์ปัจจุบันก่อน (ถ้ามีคอลัมน์ที่ชื่อซ้ำแต่เป็นช่องว่างอยู่)
            curr_working_clean = curr_working.drop(columns=[col for col in extra_db_cols if col in curr_working.columns], errors="ignore")
            
            # ทำการรวมไฟล์โดยยึดฝั่งฐานข้อมูล (Database) เป็นหลัก เพื่อให้ดึงมาครบทุก Row ใน database
            df_result = pd.merge(
                curr_working_clean,
                db_working,
                on=join_keys,
                how="right"
            )
            
            # จัดตำแหน่งให้คอลัมน์เงื่อนไขหลักไปอยู่ด้านหน้าสุด
            final_cols_order = join_keys + [col for col in df_result.columns if col not in join_keys]
            df_result = df_result[final_cols_order]
            
            # หากช่องไหนในตารางไม่มีข้อมูลจับคู่ ให้ใส่เครื่องหมาย "-"
            for col in df_result.columns:
                df_result[col] = df_result[col].fillna("-")
                
            st.success(f"✅ ดึงข้อมูลสำเร็จ! รวมผลลัพธ์จากฐานข้อมูลต้นทางทั้งหมด {len(df_result)} แถว")
            
            st.markdown("### 📋 3. ตารางผลลัพธ์ข้อมูลเวอร์ชันสมบูรณ์")
            st.dataframe(df_result)
            
            # แปลงข้อมูลกลับเป็น Excel สำหรับดาวน์โหลด
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='AMR_Matched_Data')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ผลลัพธ์เวอร์ชันอัปเดต (Excel)",
                data=processed_data,
                file_name="amr_flexible_matched_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดทางเทคนิคในการประมวลผล: {e}")
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มตั้งค่าจับคู่คอลัมน์")
