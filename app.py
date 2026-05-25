import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AMR Auto Price Matcher", layout="wide")

st.title("📦 AMR Auto Product Price Matching System (Smart Fallback Mode)")
st.markdown("""
ระบบจับคู่และกรอกราคาขาย (**SALE PRICE**) อัตโนมัติแบบคลิกเดียวจบ **เวอร์ชันแก้ไขปัญหา Not Found อัจฉริยะ**
- **รอบที่ 1:** จับคู่แบบแม่นยำสูงด้วย 4 เงื่อนไข (`TYPE OF PRODUCT` + `PACKAGING` + `MATERIAL` + `RATIO`)
- **รอบที่ 2 (Fallback):** ถ้ารายการไหนไม่เจอ จะดึงราคาใหม่อัตโนมัติด้วย 3 เงื่อนไขหลัก เพื่อให้ได้ราคาครบถ้วนที่สุด
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
    return series.astype(str).str.strip().str.upper()\
                 .str.replace(" ", "", regex=False)\
                 .str.replace("-", "", regex=False)\
                 .str.replace("_", "", regex=False)\
                 .str.replace(".", "", regex=False)\
                 .str.replace("/", "", regex=False)\
                 .replace(["NONE", "NAN", ""], "EMPTY")

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

    st.subheader("📊 1. ตรวจสอบไฟล์ที่อัปโหลด (ระบบตรวจจับคอลัมน์อัตโนมัติ)")
    
    # ฝั่งข้อมูลปัจจุบันขอแค่มี 3 คอลัมน์หลักก็ยอมให้ทำงานได้ ส่วน RATIO มีหรือไม่มีก็ได้
    db_ready = db_type_col and db_pkg_col and db_mat_col and db_price_col
    curr_ready = curr_type_col and curr_pkg_col and curr_mat_col

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🗃️ **ไฟล์ฐานข้อมูล (Database) มีทั้งหมด: {len(df_db)} แถว**")
        if db_ready:
            st.success("🔍 พบคอลัมน์หลักฝั่ง Database เรียบร้อยแล้ว")
            st.text(f"- ประเภท: {db_type_col} | บรรจุภัณฑ์: {db_pkg_col} | วัสดุ: {db_mat_col}")
            st.text(f"- อัตราส่วน (RATIO): {db_ratio_col if db_ratio_col else 'ไม่พบ (จะใช้ระบบ Fallback แทน)'} | ราคา: {db_price_col}")
        else:
            st.error("❌ ฝั่ง Database: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_db)
        
    with col2:
        st.markdown(f"📄 **ไฟล์ปัจจุบันที่ต้องการเติมราคา มีทั้งหมด: {len(df_curr)} แถว**")
        if curr_ready:
            st.success("🔍 พบคอลัมน์หลักฝั่ง ไฟล์ปัจจุบัน เรียบร้อยแล้ว")
            st.text(f"- ประเภท: {curr_type_col} | บรรจุภัณฑ์: {curr_pkg_col} | วัสดุ: {curr_mat_col}")
            st.text(f"- อัตราส่วน (RATIO): {curr_ratio_col if curr_ratio_col else 'ไม่พบ'}")
        else:
            st.error("❌ ฝั่ง ไฟล์ปัจจุบัน: ตรวจหาคอลัมน์หลักบางคอลัมน์ไม่เจอ")
        st.dataframe(df_curr)

    if not db_ready or not curr_ready:
        st.warning("⚠️ โปรดตรวจสอบคอลัมน์ของทั้ง 2 ไฟล์ให้มีฟิลด์ประเภท บรรจุภัณฑ์ และวัสดุ เป็นอย่างน้อยครับ")
    else:
        st.markdown("---")
        if st.button("🚀 เริ่มต้นดึงข้อมูลราคาขายอัตโนมัติ (Run Smart Fallback Match)"):
            
            db_working = df_db.copy()
            df_final_output = df_curr.copy()
            
            # ลบคอลัมน์ราคาขายเดิมที่มีอยู่ในไฟล์ปัจจุบันออกก่อน (ป้องกันคอลัมน์ซ้ำ)
            cols_to_drop = []
            for c in df_final_output.columns:
                c_upper = str(c).strip().upper().replace(" ", "")
                if c_upper in ["SALEPRICE", "PRICE", "ราคาขาย", "ราคา"]:
                    cols_to_drop.append(c)
            df_final_output = df_final_output.drop(columns=cols_to_drop, errors="ignore")
            
            # เตรียมคีย์ทำความสะอาดชั่วคราวสำหรับดึงข้อมูล
            db_working["join_type"] = normalize_series(db_working[db_type_col])
            db_working["join_pkg"] = normalize_series(db_working[db_pkg_col])
            db_working["join_mat"] = normalize_series(db_working[db_mat_col])
            
            df_final_output["join_type"] = normalize_series(df_final_output[curr_type_col])
            df_final_output["join_pkg"] = normalize_series(df_final_output[curr_pkg_col])
            df_final_output["join_mat"] = normalize_series(df_final_output[curr_mat_col])
            
            # ตรวจสอบเงื่อนไข RATIO
            has_ratio = db_ratio_col is not None and curr_ratio_col is not None
            if has_ratio:
                db_working["join_ratio"] = normalize_series(db_working[db_ratio_col])
                df_final_output["join_ratio"] = normalize_series(df_final_output[curr_ratio_col])
            
            # --- รอบที่ 1: ค้นหาแบบ 4 เงื่อนไข (หรือ 3 เงื่อนไขหลักถ้าไม่มีคอลัมน์ RATIO) ---
            keys_round1 = ["join_type", "join_pkg", "join_mat", "join_ratio"] if has_ratio else ["join_type", "join_pkg", "join_mat"]
            df_db_r1 = db_working[keys_round1 + [db_price_col]].drop_duplicates(subset=keys_round1, keep='last')
            df_db_r1 = df_db_r1.rename(columns={db_price_col: "SALE PRICE_R1"})
            
            df_result = pd.merge(df_final_output, df_db_r1, on=keys_round1, how="left")
            
            # --- รอบที่ 2: ค้นหาแบบ Fallback (3 เงื่อนไขหลัก) เพื่อเก็บตกกรณีค่า RATIO ไม่ตรงกัน ---
            keys_round2 = ["join_type", "join_pkg", "join_mat"]
            df_db_r2 = db_working[keys_round2 + [db_price_col]].drop_duplicates(subset=keys_round2, keep='last')
            df_db_r2 = df_db_r2.rename(columns={db_price_col: "SALE PRICE_R2"})
            
            df_result = pd.merge(df_result, df_db_r2, on=keys_round2, how="left")
            
            # เลือกใช้ราคาจากรอบที่ 1 ก่อน ถ้ารอบที่ 1 ไม่มี ค่อยดึงรอบที่ 2 มาใส่แทน
            df_result["SALE PRICE"] = df_result["SALE PRICE_R1"].fillna(df_result["SALE PRICE_R2"])
            
            # ลบคอลัมน์ที่ใช้ประมวลผลชั่วคราวออกให้ตารางสะอาด
            cols_clean = ["join_type", "join_pkg", "join_mat", "join_ratio", "SALE PRICE_R1", "SALE PRICE_R2"]
            df_result = df_result.drop(columns=cols_clean, errors="ignore")
            df_result = df_result.loc[:, ~df_result.columns.duplicated()]
            
            # เติมคำว่า Not Found ในจุดที่หาไม่เจอจริง ๆ ทั้งสองรอบ
            df_result["SALE PRICE"] = df_result["SALE PRICE"].fillna("Not Found")
            
            # นับจำนวนผลลัพธ์
            is_found_mask = df_result["SALE PRICE"].astype(str) != "Not Found"
            found_count = int(is_found_mask.values.sum())
            total_rows = len(df_result)
            not_found_count = total_rows - found_count
            
            st.success("✅ ประมวลผลสำเร็จ! ดึงข้อมูลราคาขายด้วยระบบจับคู่อัจฉริยะ 2 ชั้นเรียบร้อยแล้ว")
            st.info(f"📋 จำนวนแถวผลลัพธ์ทั้งหมด: {total_rows} แถว | เจอราคา: {found_count} รายการ | ไม่เจอราคา: {not_found_count} รายการ")
            
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
