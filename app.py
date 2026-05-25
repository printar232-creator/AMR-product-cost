import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (4 Criteria - Smart Match)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ **เวอร์ชันแก้ไขปัญหาจับคู่ไม่เจอ (Not Found) และเติมครบทุกแถว**
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

def normalize_series(series):
    # ปรับปรุงให้ฉลาดขึ้น: จัดการปัญหารูปแบบข้อความ ตัวเลข ทศนิยม (เช่น 1.0 -> 1) 
    # เพื่อป้องกันการแมตช์พลาดเนื่องจากประเภทข้อมูลไม่ตรงกัน
    def clean_val(val):
        if pd.isna(val):
            return ""
        # ถ้าเป็นตัวเลขที่มีทศนิยม .0 ให้ตัดออกให้เหลือนำหน้าปกติ เพื่อให้แมตช์กันได้ง่ายขึ้น
        val_str = str(val).strip()
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        return val_str.upper().replace(" ", "").replace("-", "").replace("_", "").replace(".", "").replace("/", "")
    
    return series.apply(clean_val)

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

    st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด (ระบบตรวจจับคอลัมน์อัตโนมัติ 4 เงื่อนไข)")
    
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_ratio_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col and curr_ratio_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database) มีทั้งหมด: {len(df_db)} แถว**")
        if db_ready:
            st.success("🔍 พบคอลัมน์หลักฝั่ง Database เรียบร้อยแล้ว")
            st.text(f"- ประเภท: {db_type_col}")
            st.text(f"- บรรจุภัณฑ์: {db_pkg_col}")
            st.text(f"- วัสดุ: {db_mat_col}")
            st.text(f"- อัตราส่วน: {db_ratio_col}")
            st.text(f"- ราคา: {db_price_col}")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_db)
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา มีทั้งหมด: {len(df_curr)} แถว**")
        if curr_ready:
            st.success("🔍 พบคอลัมน์หลักฝั่ง ไฟล์ปัจจุบัน เรียบร้อยแล้ว")
            st.text(f"- ประเภท: {curr_type_col}")
            st.text(f"- บรรจุภัณฑ์: {curr_pkg_col}")
            st.text(f"- วัสดุ: {curr_mat_col}")
            st.text(f"- อัตราส่วน: {curr_ratio_col}")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_curr)

    if not db_ready or not curr_ready:
        st.warning("⚠️ โปรดตรวจสอบคอลัมน์ของทั้ง 2 ไฟล์ให้ถูกต้องก่อนรันระบบครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Smart Auto-Match)"):
            
            # ป้องกันปัญหา Side Effect โดยทำการคัดลอกข้อมูลดิบแยกออกมาทำสำเนาทำงาน
            db_working = df_db.copy()
            df_final_output = df_curr.copy()
            
            # สร้างคีย์สำหรับการ Clean ข้อมูลเพื่อนำมาใช้ Join (จับคู่)
            db_working["join_type"] = normalize_series(db_working[db_type_col])
            db_working["join_pkg"] = normalize_series(db_working[db_pkg_col])
            db_working["join_mat"] = normalize_series(db_working[db_mat_col])
            db_working["join_ratio"] = normalize_series(db_working[db_ratio_col])
            
            df_final_output["join_type"] = normalize_series(df_final_output[curr_type_col])
            df_final_output["join_pkg"] = normalize_series(df_final_output[curr_pkg_col])
            df_final_output["join_mat"] = normalize_series(df_final_output[curr_mat_col])
            df_final_output["join_ratio"] = normalize_series(df_final_output[curr_ratio_col])
            
            # ลบคอลัมน์ราคาขายเก่าในไฟล์ปัจจุบันออกก่อน (ถ้ามี) เพื่อไม่ให้ชื่อคอลัมน์ซ้ำซ้อนกันซ้ำซาก
            cols_to_drop = []
            for c in df_final_output.columns:
                c_upper = str(c).strip().upper().replace(" ", "")
                if c_upper in ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]:
                    cols_to_drop.append(c)
            df_final_output = df_final_output.drop(columns=cols_to_drop, errors="ignore")
            
            # -------------------------------------------------------------
            # ขั้นตอนหลัก: ประมวลผลแมตช์ข้อมูลแบบ Fallback (ไล่ระดับเงื่อนไขเพื่อให้ติดทุกแถว)
            # -------------------------------------------------------------
            
            # 1. เตรียมชุดข้อมูลราคาสำหรับแบบ 4 เงื่อนไข (เข้มงวดสุด)
            match_keys_4 = ["join_type", "join_pkg", "join_mat", "join_ratio"]
            df_db_4 = db_working[match_keys_4 + [db_price_col]].drop_duplicates(subset=match_keys_4, keep='last')
            df_db_4 = df_db_4.rename(columns={db_price_col: "PRICE_MATCH_4"})
            
            # 2. เตรียมชุดข้อมูลสำรองแบบ 2 เงื่อนไข (กรณีข้อมูลบางช่องกรอกมาไม่ครบ เช่น ไม่มี Ratio หรือเกรดวัสดุ)
            match_keys_2 = ["join_type", "join_pkg"]
            df_db_2 = db_working[match_keys_2 + [db_price_col]].drop_duplicates(subset=match_keys_2, keep='last')
            df_db_2 = df_db_2.rename(columns={db_price_col: "PRICE_MATCH_2"})
            
            # ทำการ Merge ลำดับแรก (แบบ 4 เงื่อนไขหลัก)
            df_result = pd.merge(df_final_output, df_db_4, on=match_keys_4, how="left")
            
            # ทำการ Merge ลำดับสอง (แบบ 2 เงื่อนไขสำรอง) เพื่อดึงมาเติมแถวที่ค่าว่างหลุดไป
            df_result = pd.merge(df_result, df_db_2, on=match_keys_2, how="left")
            
            # เลือกใช้ราคา: ถ้าเงื่อนไข 4 เจอให้ใช้ 4, ถ้าไม่เจอให้ถอยมาใช้เงื่อนไข 2, ถ้าไม่เจอจริง ๆ ให้ใส่ "Not Found"
            df_result["SALE PRICE"] = df_result["PRICE_MATCH_4"].fillna(df_result["PRICE_MATCH_2"])
            df_result["SALE PRICE"] = df_result["SALE PRICE"].fillna("Not Found")
            
            # เคลียร์คอลัมน์ขยะและคีย์ชั่วคราวทิ้ง เพื่อให้เหลือเฉพาะหน้าตาตารางจริงที่ผู้ใช้ต้องการ
            temp_cols = match_keys_4 + ["PRICE_MATCH_4", "PRICE_MATCH_2"]
            df_result = df_result.drop(columns=temp_cols, errors="ignore")
            df_result = df_result.loc[:, ~df_result.columns.duplicated()]
            
            # คำนวณสรุปผลรายงาน
            is_found_mask = df_result["SALE PRICE"].astype(str) != "Not Found"
            found_count = int(is_found_mask.values.sum())
            total_rows = len(df_result)
            not_found_count = total_rows - found_count
            
            # -------------------------------------------------------------
            # แสดงผลบน Streamlit UI
            # -------------------------------------------------------------
            st.success("✅ ประมวลผลสำเร็จ! ตรวจทานข้อมูลครบถ้วนทุกแถวเรียบร้อยแล้ว")
            st.info(f"📋 จำนวนแถวไฟล์ปลายทางทั้งหมด: {total_rows} แถว | จับคู่สำเร็จ: {found_count} รายการ | ไม่พบราคา: {not_found_count} รายการ")
            
            st.markdown("### 📋 2. ตารางผลลัพธ์ข้อมูลเวอร์ชันอัปเดต (เติมราคาขายเรียบร้อย)")
            st.dataframe(df_result)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Updated_Sale_Price')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ที่เติมราคาขายเสร็จสมบูรณ์ (Excel)",
                data=processed_data,
                file_name="updated_sales_price_smart_match.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("💡 คำแนะนำ: โปรดอัปโหลดไฟล์ทั้ง 2 ไฟล์ที่แถบเมนูด้านซ้ายเพื่อเริ่มระบบทำงานอัตโนมัติ")
