from utils.db_helper import get_db_connection

class ServiceService:
    
    def save_service_scd2(self, service_name: str, container_key: str, from_date: str, to_date: str, unit_price: int, tax_rate: int) -> bool:
        if not service_name or not container_key or not from_date or not to_date:
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            cursor.execute(
                "SELECT service_key, service_name, container_key, from_date, to_date, unit_price, tax_rate FROM dbo.services WHERE service_name = ? AND container_key = ? AND from_date = ? AND to_date = ? AND is_active = N'Y'",
                (service_name, container_key, from_date, to_date)
            )
            existing_service = cursor.fetchone()
            
            if existing_service:
                old_service_key = existing_service[0]
                old_service_name = existing_service[1] or ""
                old_container_key = str(existing_service[2] or "")
                old_from_date = str(existing_service[3] or "")
                old_to_date = str(existing_service[4] or "")
                old_unit_price = existing_service[5] or 0
                old_tax_rate = existing_service[6] or 0
                
                service_name_clean = str(service_name or "").strip()
                container_key_clean = str(container_key or "").strip()
                from_date_clean = str(from_date or "").strip()
                to_date_clean = str(to_date or "").strip()
                unit_price_clean = int(unit_price or 0)
                tax_rate_clean = int(tax_rate or 0)
                
                old_service_name_clean = str(old_service_name or "").strip()
                old_container_key_clean = str(old_container_key or "").strip()
                old_from_date_clean = str(old_from_date or "").strip()
                old_to_date_clean = str(old_to_date or "").strip()
                old_unit_price_clean = int(old_unit_price or 0)
                old_tax_rate_clean = int(old_tax_rate or 0)
                
                has_changes = (
                    service_name_clean != old_service_name_clean or
                    container_key_clean != old_container_key_clean or
                    from_date_clean != old_from_date_clean or
                    to_date_clean != old_to_date_clean or
                    unit_price_clean != old_unit_price_clean or
                    tax_rate_clean != old_tax_rate_clean
                )
                
                if not has_changes:
                    conn.commit()
                    conn.close()
                    print(f"[ServiceService] Service ({service_name}, {container_key}) has no changes, skipping append.")
                    return True
                
                cursor.execute("SELECT CURRENT_TIMESTAMP")
                current_timestamp = cursor.fetchone()[0]
                
                cursor.execute(
                    "UPDATE dbo.services SET end_time = ?, is_active = N'N' WHERE service_key = ?",
                    (current_timestamp, old_service_key)
                )
                
                cursor.execute(
                    """INSERT INTO dbo.services (service_name, container_key, from_date, to_date, unit_price, tax_rate, start_time, end_time, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, ?, NULL, N'Y')""",
                    (service_name, container_key, from_date, to_date, unit_price, tax_rate, current_timestamp)
                )
            else:
                cursor.execute(
                    """INSERT INTO dbo.services (service_name, container_key, from_date, to_date, unit_price, tax_rate, start_time, end_time, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, NULL, N'Y')""",
                    (service_name, container_key, from_date, to_date, unit_price, tax_rate)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ServiceService] Error saving service: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

