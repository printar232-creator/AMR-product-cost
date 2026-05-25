import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AMR Product Pricing Matcher", layout="wide")

st.title("📦 ระบบบันทึกใบส่งสินค้าชั่วคราว & คำนวณราคาขาย (AMR)")
st.write("อัปโหลดไฟล์รายการส่งสินค้าชั่วคราวเพื่อเติมช่อง **SALE PRICE** โดยอัตโนมัติจากฐานข้อมูลราคา")

# 1. Database Loading Section
DB_FILENAME = "database for product cost AMR.xlsx"

@st.cache_data
def load_database(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df_db = pd.read_excel(file_path)
        df_db.columns = df_db.columns.str.strip().str.upper()
        return df_db
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

df_db = load_database(DB_FILENAME)

if df_db is None:
    st.warning(f"⚠️ ไม่พบไฟล์ฐานข้อมูล {DB_FILENAME} ในระบบ กรุณาตรวจสอบการอัปโหลด")
else:
    st.success(f"✅ โหลดฐานข้อมูลสินค้า {DB_FILENAME} เรียบร้อยแล้ว")
    with st.expander("ดูข้อมูลฐานข้อมูลราคาต้นทุน/ราคาขาย (Database)"):
        st.dataframe(df_db.head())

st.markdown("---")

# 2. File Upload & Processing Section
uploaded_file = st.file_uploader("📂 ลากและวาง หรือเลือกไฟล์ใบส่งสินค้าชั่วคราวประจำเดือน (.xlsx, .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
            
        st.subheader("📋 ตัวอย่างข้อมูลที่อัปโหลดเข้ามา")
        st.dataframe(df_input.head())
        
        df_proc = df_input.copy()
        df_proc.columns = df_proc.columns.str.strip().str.upper()
        
        required_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]
        missing_cols = [col for col in required_cols if col not in df_proc.columns]
        
        if missing_cols:
            st.error(f"❌ ไม่พบคอลัมน์ที่จำเป็นในไฟล์ที่นำเข้า: {', '.join(missing_cols)}")
        else:
            if st.button("🚀 เริ่มประมวลผลจับคู่ราคา SALE PRICE"):
                with st.spinner("กำลังประมวลผล..."):
                    db_cols = ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL", "SALE PRICE"]
                    
                    if not all(col in df_db.columns for col in db_cols):
                        st.error("❌ โครงสร้างตารางในไฟล์ฐานข้อมูลกลางไม่ถูกต้อง")
                    else:
                        df_db_clean = df_db[db_cols].drop_duplicates(subset=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"])
                        
                        for col in ["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"]:
                            df_proc[col] = df_proc[col].astype(str).str.strip()
                            df_db_clean[col] = df_db_clean[col].astype(str).str.strip()
                        
                        if "SALE PRICE" in df_proc.columns:
                            df_proc = df_proc.drop(columns=["SALE PRICE"])
                            
                        df_result_proc = pd.merge(df_proc, df_db_clean, on=["TYPE OF PRODUCT", "PAKAGING", "MATERIAL"], how="left")
                        
                        df_final = df_input.copy()
                        df_final["SALE PRICE"] = df_result_proc["SALE PRICE"]
                        
                        st.subheader("✨ Preview")
                        st.dataframe(df_final)
                        
                        matched_count = df_final["SALE PRICE"].notna().sum()
                        unmatched_count = df_final["SALE PRICE"].isna().sum()
                        st.info(f"📊 Match: {matched_count} | Unmatch: {unmatched_count}")
                        
                        import io
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_final.to_excel(writer, index=False, sheet_name='Sheet1')
                        excel_data = output.getvalue()
                        
                        raw_filename = uploaded_file.name.split('.')[0]
                        out_filename = f"Processed_{raw_filename}.xlsx"
                        
                        st.download_button(
                            label="📥 ดาวน์โหลดไฟล์ผลลัพธ์ใบส่งสินค้าใหม่ (.xlsx)",
                            data=excel_data,
                            file_name=out_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
    except Exception as e:
        st.error(f"Error: {e}")
