import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ 
โดยระบบจะสแกนหาและจับคู่จาก 3 หัวข้อหลักให้อัตโนมัติ:
1. **TYPE OF PRODUCT** | 2. **PACKAGING** | 3. **MATERIAL**
""")

st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

# ฟังก์ชันพิเศษช่วยค้นหาคอลัมน์ที่ใกล้เคียงที่สุดในกรณีที่สะกดไม่ตรงเป๊ะ
def find_smart_column(df_columns, target_keywords):
    for col in df_columns:
        col_clean = str(col).strip().upper().replace(" ", "").replace("_", "").replace("-", "")
        for kw in target_keywords:
            if kw in col_clean:
                return col
    return None

if db_file and curr_file:
    # อ่านไฟล์โดยล้างแถวว่างด้านบนออกอัตโนมัติ เพื่อป้องกันกรณีหัวตารางไม่ได้อยู่บรรทัดแรก
    df_db = pd.read_excel(db_file)
    df_curr = pd.read_excel(curr_file)
    
    # กำหนด Keyword ที่มีโอกาสเจอในระบบ
    type_kws = ["TYPEOFPRODUCT", "PRODUCTTYPE", "PRODUCT", "ประเภทสินค้า", "ชนิดสินค้า"]
    pkg_kws = ["PACKAGING", "PKG", "PACKAGE", "บรรจุภัณฑ์", "แพ็คเกจ", "ถุง"]
    mat_kws = ["MATERIAL", "MAT", "GRADE", "วัสดุ", "เกรด"]
    price_kws = ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]

    # ค้นหาชื่อคอลัมน์จริงจากไฟล์ของฝั่ง Database
    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_price_col = find_smart_column(df_db.columns, price_kws)

    # ค้นหาชื่อคอลัมน์จริงจากไฟล์ของฝั่ง ไฟล์ปัจจุบัน
    curr_type_col = find_smart_column(df_curr.columns, type_kws)
    curr_pkg_col = find_smart_column(df_curr.columns, pkg_kws)
    curr_mat_col = find_smart_column(df_curr.columns, mat_kws)

    st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด (ระบบตรวจจับคอลัมน์อัตโนมัติ)")
    
    # ตรวจสอบความพร้อมของคอลัมน์
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database): {len(df_db)} แถว**")
        if db_ready:
            st.success(f"🔍 ตรวจพบคอลัมน์หลักครบถ้วน:\n- ประเภท: `{db_type_col}`\n- บรรจุภัณฑ์: `{db_pkg_col}`\n- วัสดุ: `{db_mat_col}`\n- ราคา: `{db_price_col}`")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ โปรดเช็คชื่อหัวตารางใน Excel")
        st.dataframe(df_db.head(5))
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา: {len(df_curr)} แถว**")
        if curr_ready:
            st.success(f"🔍 ตรวจพบคอลัมน์หลักครบถ้วน:\n- ประเภท: `{curr_type_col}`\n- บรรจุภัณฑ์: `{curr_pkg_col}`\n- วัสดุ: `{curr_mat_col}`")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ โปรดเช็คชื่อหัวตารางใน Excel")
        st.dataframe(df_curr.head(5))

    if not db_ready or not curr_ready:
        st.warning("⚠️ วิธีแก้ไขในไฟล์ Excel ของคุณ: โปรดเปิดไฟล์ Excel ขึ้นมาดู แล้วแก้ไขชื่อหัวข้อ (Row แรกสุดของตาราง) ให้มีคำว่า TYPE OF PRODUCT, PACKAGING, MATERIAL หรือคำที่ใกล้เคียง จากนั้นค่อยอัปโหลดใหม่อีกครั้งครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Auto-Match)"):
            
            # คัดลอกข้อมูลมาประมวลผล
            db_working = df_db.copy()
            curr_working = df_curr.copy()
            
            # แปลงข้อมูลในคอลัมน์หลักให้เป็นข้อความดิบและตัดเว้นวรรค
            db_working[db_type_col] = db_working[db_type_col].astype(str).str.strip()
            db_working[db_pkg_col] = db_working[db_pkg_col].astype(str).str.strip()
            db_working[db_mat_col] = db_working[db_mat_col].astype(str).str.strip()
            
            curr_working[curr_type_col] = curr_working[curr_type_col].astype(str).str.strip()
            curr_working[curr_pkg_col] = curr_working[curr_pkg_col].astype(str).str.strip()
            curr_working[curr_mat_col] = curr_working[curr_mat_col].astype(str).str.strip()
            
            # เปลี่ยนชื่อคอลัมน์ฝั่ง Database ให้ตรงกับไฟล์ปัจจุบันเพื่อทำโครงสร้าง Merge
            rename_dict = {
                db_type_col: curr_type_col,
                db_pkg_col: curr_pkg_col,
                db_mat_col: curr_mat_col,
                db_price_col: "SALE PRICE"
            }
            db_working = db_working.rename(columns=rename_dict)
            
            # คีย์หลักในการจับคู่
            join_keys = [curr_type_col, curr_pkg_col, curr_mat_col]
            
            # ดึงเฉพาะคีย์หลักและคอลัมน์ราคาขาย ลบข้อมูลซ้ำซ้อน
            df_db_prices = db_working[join_keys + ["SALE PRICE"]].drop_duplicates(subset=join_keys, keep='last')
            
            # ลบคอลัมน์ราคาเดิมในไฟล์ปัจจุบันออกก่อน (ถ้ามี)
            curr_working_clean = curr_working.drop(columns=["SALE PRICE"], errors="ignore")
            
            # ทำการจับคู่ข้อมูลแบบ Left Join
            df_result = pd.merge(
                curr_working_clean,
                df_db_prices,
                on=join_keys,
                how="left"
            )
            
            df_result["SALE PRICE"] = df_result["SALE PRICE"].fillna("Not Found")
            
            found_count = int((df_result["SALE PRICE"] != "Not Found").sum())
            not_found_count = int((df_result["SALE PRICE"] == "Not Found").sum())
            total_rows = len(df_result)
            
            st.success("✅ ประมวลผลสำเร็จ! เติมราคาขายเรียบร้อยแล้ว")
            st.info(f"📋 จำนวนแถวทั้งหมด: {total_rows} | เจอราคา: {found_count} รายการ | ไม่เจอราคา: {not_found_count} รายการ")
            
            st.markdown("### 📋 2. ตารางผลลัพธ์ข้อมูลที่เติมราคาขายเรียบร้อยแล้ว")
            st.dataframe(df_result)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Updated_Sale_Price')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ที่เติมราคาขายเสร็จสมบูรณ์ (Excel)",
                data=processed_data,
                file_name="updated_sales_price_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มระบบทำงานอัตโนมัติ")
