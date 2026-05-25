import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (4 Criteria - All Rows)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ **เวอร์ชันดึงข้อมูลครบทุกแถว 100%**
โดยระบบจะสแกนหาและจับคู่จาก 4 หัวข้อหลักให้อัตโนมัติ:
1. **TYPE OF PRODUCT** | 2. **PACKAGING** | 3. **MATERIAL** | 4. **RATIO**
""")

st.sidebar.header("📁 อัปโหลดไฟล์ข้อมูล")
db_file = st.sidebar.file_uploader("1. ไฟล์ฐานข้อมูลต้นทาง (database for product cost AMR.xlsx)", type=["xlsx"])
curr_file = st.sidebar.file_uploader("2. ไฟล์ข้อมูลปัจจุบันที่ต้องการเติมราคา", type=["xlsx"])

def find_smart_column(df_columns, target_keywords):
    for col in df_columns:
        col_clean = str(col).strip().upper().replace(" ", "").replace("_", "").replace("-", "")
        for kw in target_keywords:
            if kw in col_clean:
                return col
    return None

if db_file and curr_file:
    df_db = pd.read_excel(db_file)
    df_curr = pd.read_excel(curr_file)
    
    type_kws = ["TYPEOFPRODUCT", "PRODUCTTYPE", "PRODUCT", "ประเภทสินค้า", "ชนิดสินค้า"]
    pkg_kws = ["PACKAGING", "PKG", "PACKAGE", "บรรจุภัณฑ์", "แพ็คเกจ", "ถุง"]
    mat_kws = ["MATERIAL", "MAT", "GRADE", "วัสดุ", "เกรด"]
    ratio_kws = ["RATIO", "อัตราส่วน", "สัดส่วน", "เปอร์เซ็นต์", "MESH"]
    price_kws = ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]

    db_type_col = find_smart_column(df_db.columns, type_kws)
    db_pkg_col = find_smart_column(df_db.columns, pkg_kws)
    db_mat_col = find_smart_column(df_db.columns, mat_kws)
    db_ratio_col = find_smart_column(df_db.columns, ratio_kws)
    db_price_col = find_smart_column(df_db.columns, price_kws)

    curr_type_col = find_smart_column(df_curr.columns, type_kws)
    curr_pkg_col = find_smart_column(df_curr.columns, pkg_kws)
    curr_mat_col = find_smart_column(df_curr.columns, mat_kws)
    curr_ratio_col = find_smart_column(df_curr.columns, ratio_kws)
    # ค้นหาว่าไฟล์ปัจจุบันแอบมีคอลัมน์ราคาเดิมอยู่ด้วยหรือไม่
    curr_price_col = find_smart_column(df_curr.columns, price_kws)

    st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด (ระบบตรวจจับคอลัมน์อัตโนมัติ 4 เงื่อนไข)")
    
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_ratio_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col and curr_ratio_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database) มีทั้งหมด: {len(df_db)} แถว**")
        if db_ready:
            st.success(f"🔍 พบคอลัมน์หลัก:\n- ประเภท=`{db_type_col}`\n- บรรจุภัณฑ์=`{db_pkg_col}`\n- วัสดุ=`{db_mat_col}`\n- อัตราส่วน=`{db_ratio_col}`\n- ราคา=`{db_price_col}`")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_db)
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา มีทั้งหมด: {len(df_curr)} แถว**")
        if curr_ready:
            st.success(f"🔍 พบคอลัมน์หลัก:\n- ประเภท=`{curr_type_col}`\n- บรรจุภัณฑ์=`{curr_pkg_col}`\n- วัสดุ=`{curr_mat_col}`\n- อัตราส่วน=`{curr_ratio_col}`")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_curr)

    if not db_ready or not curr_ready:
        st.warning("⚠️ โปรดตรวจสอบให้แน่ใจว่าทั้ง 2 ไฟล์มีชื่อหัวคอลัมน์เกี่ยวกับ RATIO หรือ อัตราส่วน เพื่อให้ระบบทำงานต่อได้ครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Auto-Match 4 Criteria)"):
            
            db_working = df_db.copy()
            curr_working = df_curr.copy()
            
            for col in [db_type_col, db_pkg_col, db_mat_col, db_ratio_col]:
                db_working[col] = db_working[col].astype(str).str.strip()
                
            for col in [curr_type_col, curr_pkg_col, curr_mat_col, curr_ratio_col]:
                curr_working[col] = curr_working[col].astype(str).str.strip()
            
            rename_dict = {
                db_type_col: curr_type_col,
                db_pkg_col: curr_pkg_col,
                db_mat_col: curr_mat_col,
                db_ratio_col: curr_ratio_col,
                db_price_col: "SALE PRICE"
            }
            db_working = db_working.rename(columns=rename_dict)
            
            join_keys = [curr_type_col, curr_pkg_col, curr_mat_col, curr_ratio_col]
            
            df_db_prices = db_working[join_keys + ["SALE PRICE"]].drop_duplicates(subset=join_keys, keep='last')
            
            # ✅ แก้ไขปัญหารายการซ้ำ: สั่งลบคอลัมน์ราคาเดิมทุกรูปแบบที่ตรวจเจอในไฟล์ปัจจุบันออกไปก่อน เพื่อไม่ให้ชื่อซ้ำกันตอน Merge
            columns_to_drop = ["SALE PRICE"]
            if curr_price_col and curr_price_col in curr_working.columns:
                columns_to_drop.append(curr_price_col)
            
            curr_working_clean = curr_working.drop(columns=columns_to_drop, errors="ignore")
            
            df_result = pd.merge(
                curr_working_clean,
                df_db_prices,
                on=join_keys,
                how="left"
            )
            
            df_result["SALE PRICE"] = df_result["SALE PRICE"].fillna("Not Found")
            
            is_found_mask = df_result["SALE PRICE"].astype(str) != "Not Found"
            found_count = int(is_found_mask.values.sum())
            total_rows = len(df_result)
            not_found_count = total_rows - found_count
            
            st.success("✅ ประมวลผลสำเร็จ! ดึงข้อมูลครบทุกแถวโดยอ้างอิง 4 เงื่อนไขเรียบร้อยแล้ว")
            st.info(f"📋 จำนวนแถวผลลัพธ์ทั้งหมด: {total_rows} แถว | เจอราคา: {found_count} รายการ | ไม่เจอราคา: {not_found_count} รายการ")
            
            st.markdown("### 📋 2. ตารางผลลัพธ์ข้อมูลเวอร์ชันอัปเดต (เทียบ 4 เงื่อนไข)")
            st.dataframe(df_result)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Updated_Sale_Price')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ที่เติมราคาขายเสร็จสมบูรณ์ (Excel)",
                data=processed_data,
                file_name="updated_sales_price_4_criteria.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มระบบทำงานอัตโนมัติ")
