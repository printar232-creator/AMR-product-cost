# จัดการข้อมูลฝั่งผู้ใช้ให้ไม่มีช่องว่างส่วนเกิน
                for col in required_cols:
                    df_user[col] = df_user[col].astype(str).str.strip()
                
                # --- จุดที่แก้ไข: เช็คคอลัมน์ SALE PRICE ให้หัวข้ออยู่ในบรรทัดเดียวกันอย่างถูกต้อง ---
                if 'SALE PRICE' not in df_database.columns:
                    st.error("❌ ไม่พบคอลัมน์ 'SALE PRICE' ในไฟล์ Database บน GitHub")
                else:
                    # เตรียมคอลัมน์สำหรับการ Mapping (เลือกเฉพาะ Key และ Target)
                    df_db_mapping = df_database[['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL', 'SALE PRICE']].drop_duplicates()
                    
                    # ถ้าไฟล์เดิมของผู้ใช้มีคอลัมน์ SALE PRICE อยู่แล้ว ให้ลบออกก่อนเพื่อใส่ค่าที่อัพเดทใหม่เข้าไป
                    if 'SALE PRICE' in df_user.columns:
                        df_user = df_user.drop(columns=['SALE PRICE'])
                    
                    # ทำการ Merge ข้อมูลด้วย 3 เงื่อนไข
                    df_result = pd.merge(
                        df_user, 
                        df_db_mapping, 
                        on=['TYPE OF PRODUCT', 'PAKAGING', 'MATERIAL'], 
                        how='left'
                    )
