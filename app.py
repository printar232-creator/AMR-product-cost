if uploaded_file is not None:
        try:
            # อ่านไฟล์ที่ผู้ใชัปโหลด
            df_user = pd.read_excel(uploaded_file)
            
            # ตรวจสอบคอลัมน์ที่จำเป็นสำหรับการตรวจสอบ
            required_cols = ['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL']
            missing_cols = [col for col in required_cols if col not in df_user.columns]
            
            if missing_cols:
                st.error(f"❌ ไฟล์ที่อัปโหลดไม่มีคอลัมน์ต่อไปนี้: {', '.join(missing_cols)}")
            else:
                st.info("กำลังประมวลผลคำนวณ SALE PRICE...")
                
                # --- เช็คจุดนี้: บล็อก for คอลัมน์ต้องเยื้องตรงกับตรรกะในบล็อก else ---
                for col in required_cols:
                    df_user[col] = df_user[col].astype(str).str.strip()
                
                if 'SALE PRICE' not in df_database.columns:
                    st.error("❌ ไม่พบคอลัมน์ 'SALE PRICE' ในไฟล์ Database บน GitHub")
                else:
                    # เตรียมคอลัมน์สำหรับการ Mapping
                    df_db_mapping = df_database[['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']].drop_duplicates()
                    
                    if 'SALE PRICE' in df_user.columns:
                        df_user = df_user.drop(columns=['SALE PRICE'])
                    
                    # ทำการ Merge ข้อมูล
                    df_result = pd.merge(
                        df_user, 
                        df_db_mapping, 
                        on=['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL'], 
                        how='left'
                    )
                    
                    # แสดงผลลัพธ์
                    st.success("🎉 ประมวลผลและเติมช่อง SALE PRICE เรียบร้อยแล้ว!")
                    st.dataframe(df_result)
