from typing import Optional
from utils.db_helper import get_db_connection


class LineService:
    
    def get_receipt_key_by_code(self, receipt_code: str, use_test_tables: bool = False) -> Optional[str]:
        if not receipt_code:
            return None
        
        receipt_code = receipt_code.strip()[:10]
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            table_name = "test_receipts" if use_test_tables else "receipts"
            cursor.execute(
                f"SELECT receipt_key FROM dbo.{table_name} WHERE receipt_code = ?",
                (receipt_code,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"[LineService] Error getting receipt_key: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def get_service_key(self, service_name: str, container_key: str, from_date: str, to_date: str, use_test_tables: bool = False) -> Optional[str]:
        if not service_name or not container_key or not from_date or not to_date:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            table_name = "test_services" if use_test_tables else "services"
            cursor.execute(
                f"SELECT service_key FROM dbo.{table_name} WHERE service_name = ? AND container_key = ? AND from_date = ? AND to_date = ? AND is_active = N'Y'",
                (service_name, container_key, from_date, to_date)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f'[LineService] Error getting service_key: {e}')
            try:
                conn.close()
            except:
                pass
            return None
    
    def save_line(self, receipt_key: str, container_number: str, service_key: str, quantity: Optional[int], discount: Optional[int], amount: Optional[int], use_test_tables: bool = False) -> bool:
        if not receipt_key or not container_number or not service_key:
            return False
        
        container_number = container_number.strip()[:11]
        
        quantity = quantity if quantity is not None else 0
        discount = discount if discount is not None else 0
        amount = amount if amount is not None else 0
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            table_name = "test_lines" if use_test_tables else "lines"
            print(f"[LineService] use_test_tables={use_test_tables}, using table: {table_name}")
            cursor.execute(
                f"SELECT line_key, receipt_key, container_number, service_key, quantity, discount, amount FROM dbo.{table_name} WHERE receipt_key = ? AND container_number = ?",
                (receipt_key, container_number)
            )
            existing_line = cursor.fetchone()
            
            if existing_line:
                old_line_key = existing_line[0]
                old_receipt_key = existing_line[1] or ""
                old_container_number = existing_line[2] or ""
                old_service_key = existing_line[3] or ""
                old_quantity = existing_line[4] or 0
                old_discount = existing_line[5] or 0
                old_amount = existing_line[6] or 0
                
                receipt_key_clean = receipt_key.strip()
                container_number_clean = container_number.strip()
                service_key_clean = service_key.strip()
                quantity_clean = quantity
                discount_clean = discount
                amount_clean = amount
                
                old_receipt_key_clean = (old_receipt_key or "").strip()
                old_container_number_clean = (old_container_number or "").strip()
                old_service_key_clean = (old_service_key or "").strip()
                old_quantity_clean = old_quantity or 0
                old_discount_clean = old_discount or 0
                old_amount_clean = old_amount or 0
                
                has_changes = (
                    receipt_key_clean != old_receipt_key_clean or
                    container_number_clean != old_container_number_clean or
                    service_key_clean != old_service_key_clean or
                    quantity_clean != old_quantity_clean or
                    discount_clean != old_discount_clean or
                    amount_clean != old_amount_clean
                )
                
                if not has_changes:
                    conn.commit()
                    conn.close()
                    print(f"[LineService] Line with receipt_key {receipt_key} and container_number {container_number} has no changes, skipping update.")
                    return True
                
                cursor.execute(
                    f"""UPDATE dbo.{table_name} 
                       SET receipt_key = ?, container_number = ?, service_key = ?, quantity = ?, discount = ?, amount = ?
                       WHERE line_key = ?""",
                    (receipt_key, container_number, service_key, quantity, discount, amount, old_line_key)
                )
            else:
                cursor.execute(
                    f"""INSERT INTO dbo.{table_name} (receipt_key, container_number, service_key, quantity, discount, amount)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (receipt_key, container_number, service_key, quantity, discount, amount)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[LineService] Error saving line: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

