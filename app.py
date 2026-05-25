import streamlit as pd
import pandas as pd

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="AMR Product Price Matching Tool", layout="wide")

st.title("📦 ระบบเติมราคาใบส่งสินค้าชั่วคราวอัตโนมัติ (AMR)")
st.write("อัปโหลดไฟล์ใบส่งสินค้าและไฟล์ Database เพื่อคำนวณและเติมช่อง SALE PRICE")

st.divider()

# สร้าง 2 คอลัมน์สำหรับอัปโหลดไฟล์
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. ไฟล์ใบส่งสินค้าชั่วคราว")
    delivery_file = st.file_uploader("เลือกไฟล์ใบส่งสินค้า (Excel หรือ CSV)", type=["xlsx", "csv"], key="delivery")

with col2:
    st.subheader("2. ไฟล์ Database สำหรับราคาสินค้า")
    db_file = st.file_uploader("เลือกไฟล์ Database for product cost AMR", type=["xlsx", "csv"], key="database")

# เมื่ออัปโหลดครบทั้งสองไฟล์
if delivery_file and db_file:
    try:
        # --- อ่านไฟล์ใบส่งสินค้า ---
        if delivery_file.name.endswith('.xlsx'):
            df_delivery = pd.read_excel(delivery_file)
        else:
            df_delivery = pd.read_csv(delivery_file)
            
        # --- อ่านไฟล์ Database ---
        if db_file.name.endswith('.xlsx'):
            df_db = pd.read_excel(db_file)
        else:
            df_db = pd.read_csv(db_file)
            
        st.success("โหลดข้อมูลสำเร็จ! กำลังตรวจสอบคอลัมน์...")

        # กำหนดชื่อคอลัมน์ที่ต้องใช้ในการ Match
        match_cols = ['TYPE OF PRODUCT', 'PACKAGING', 'MATERIAL']
        
        # ตรวจสอบว่าคอลัมน์ที่จำเป็นมีครบหรือไม่
        missing_delivery = [col for col in match_cols if col not in df_delivery.columns]
        missing_db = [col for col in match_cols + ['SALE PRICE'] if col not in df_db.columns]
        
        if missing_delivery:
            st.error(f"❌ ไฟล์ใบส่งสินค้าขาดคอลัมน์: {', '.join(missing_delivery)}")
        elif missing_db:
            st.error(f"❌ ไฟล์ Database ขาดคอลัมน์: {', '.join(missing_db)}")
        else:
            # ลบช่องว่าง (Whitespace) ของข้อความในคอลัมน์หลักเพื่อป้องกันการ Match ไม่เจอจากเคสพิมพ์เกิน
            for col in match_cols:
                df_delivery[col] = df_delivery[col].astype(str).str.strip()
                df_db[col] = df_db[col].astype(str).str.strip()

            # สรุปข้อมูลราคาก่อนเพื่อป้องกันกรณีใน Database มีรายการซ้ำ (ดึงราคาสุดท้ายมาใช้)
            df_db_clean = df_db.drop_duplicates(subset=match_cols, keep='last')
            
            # ทำการดึงเฉพาะคอลัมน์เงื่อนไขและราคาจาก Database มาเตรียมรอ Merge
            df_db_subset = df_db_clean[match_cols + ['SALE PRICE']]
            
            # เคลียร์ช่อง SALE PRICE เดิมในไฟล์ใบส่งสินค้าออกก่อน (ถ้ามีอยู่แล้ว) เพื่อป้องกันคอลัมน์ซ้ำซ้อน
            if 'SALE PRICE' in df_delivery.columns:
                df_delivery = df_delivery.drop(columns=['SALE PRICE'])
                
            # --- ประมวลผลดึงราคา (Merge/VLOOKUP Multi-criteria) ---
            df_result = pd.merge(df_delivery, df_db_subset, on=match_cols, how='left')
            
            st.subheader("📊 ตัวอย่างข้อมูลที่ประมวลผลเสร็จแล้ว")
            st.dataframe(df_result.head(10))
            
            # นับจำนวนรายการที่หาราคาไม่เจอ (เป็นค่าว่างหรือ NaN)
            not_found_count = df_result['SALE PRICE'].isna().sum()
            if not_found_count > 0:
                st.warning(f"⚠️ มีรายการที่แมตช์ราคาไม่พบทั้งหมด {not_found_count} แถว (กรุณาตรวจสอบการสะกดคำในไฟล์)")
            else:
                st.success("✅ สามารถจับคู่ราคาได้ครบทุกรายการร้อยละ 100")
                
            # --- เตรียมสร้างไฟล์สำหรับดาวน์โหลด ---
            # แปลงไฟล์เป็น Excel ในหน่วยความจำ (Memory) ไม่บันทึกลงดิสก์ของเซิร์ฟเวอร์
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Updated_Sales')
            
            st.divider()
            
            # ปุ่มดาวน์โหลดไฟล์
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ใบส่งสินค้าที่เติมราคาแล้ว (.xlsx)",
                data=buffer.getvalue(),
                file_name="updated_delivery_with_prices.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
