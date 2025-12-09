from typing import Optional
from utils.db_helper import get_db_connection

class CustomerService:
    
    def save_customer_scd2(self, tax_code: str, customer_name: str, address: str, province_key: Optional[str], use_test_tables: bool = False) -> bool:
        if not tax_code or not customer_name:
            return False
        
        tax_code = tax_code.strip()
        
        if not province_key:
            print(f"[CustomerService] Warning: Could not find province_key for customer {customer_name} (tax_code: {tax_code}). Skipping customer save.")
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            table_name = "test_customers" if use_test_tables else "customers"
            print(f"[CustomerService] use_test_tables={use_test_tables}, using table: {table_name}")
            cursor.execute(
                f"SELECT customer_key, customer_name, address, province_key FROM dbo.{table_name} WHERE tax_code = ? AND is_active = N'Y'",
                (tax_code,)
            )
            existing_customer = cursor.fetchone()
            
            if existing_customer:
                old_customer_key = existing_customer[0]
                old_customer_name = existing_customer[1] or ""
                old_address = existing_customer[2] or ""
                old_province_key = existing_customer[3] or ""
                
                customer_name_clean = (customer_name or "").strip()
                address_clean = (address or "").strip()
                province_key_clean = (province_key or "").strip()
                
                old_customer_name_clean = (old_customer_name or "").strip()
                old_address_clean = (old_address or "").strip()
                old_province_key_clean = (old_province_key or "").strip()
                
                has_changes = (
                    customer_name_clean != old_customer_name_clean or
                    address_clean != old_address_clean or
                    province_key_clean != old_province_key_clean
                )
                
                if not has_changes:
                    conn.commit()
                    conn.close()
                    print(f"[CustomerService] Customer with tax_code {tax_code} has no changes, skipping append.")
                    return True
                
                cursor.execute("SELECT CURRENT_TIMESTAMP")
                current_timestamp = cursor.fetchone()[0]
                
                cursor.execute(
                    f"UPDATE dbo.{table_name} SET end_time = ?, is_active = N'N' WHERE customer_key = ?",
                    (current_timestamp, old_customer_key)
                )
                
                cursor.execute(
                    f"""INSERT INTO dbo.{table_name} (tax_code, customer_name, address, province_key, start_time, end_time, is_active)
                       VALUES (?, ?, ?, ?, ?, NULL, N'Y')""",
                    (tax_code, customer_name, address, province_key, current_timestamp)
                )
            else:
                cursor.execute(
                    f"""INSERT INTO dbo.{table_name} (tax_code, customer_name, address, province_key, start_time, end_time, is_active)
                       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, NULL, N'Y')""",
                    (tax_code, customer_name, address, province_key)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[CustomerService] Error saving customer: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

