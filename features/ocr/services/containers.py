from utils.db_helper import get_db_connection

class ContainerService:
    
    def save_container_scd2(self, container_size: str, container_status: str, container_type: str, use_test_tables: bool = False) -> bool:
        if not container_size or not container_status or not container_type:
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            table_name = "test_containers" if use_test_tables else "containers"
            print(f"[ContainerService] use_test_tables={use_test_tables}, using table: {table_name}")
            cursor.execute(
                f"SELECT container_key, container_size, container_status, container_type FROM dbo.{table_name} WHERE container_size = ? AND container_status = ? AND container_type = ? AND is_active = N'Y'",
                (container_size, container_status, container_type)
            )
            existing_container = cursor.fetchone()
            
            if existing_container:
                old_container_key = existing_container[0]
                old_container_size = existing_container[1] or ""
                old_container_status = existing_container[2] or ""
                old_container_type = existing_container[3] or ""
                
                container_size_clean = str(container_size or "").strip()
                container_status_clean = str(container_status or "").strip()
                container_type_clean = str(container_type or "").strip()
                
                old_container_size_clean = str(old_container_size or "").strip()
                old_container_status_clean = str(old_container_status or "").strip()
                old_container_type_clean = str(old_container_type or "").strip()
                
                has_changes = (
                    container_size_clean != old_container_size_clean or
                    container_status_clean != old_container_status_clean or
                    container_type_clean != old_container_type_clean
                )
                
                if not has_changes:
                    conn.commit()
                    conn.close()
                    print(f"[ContainerService] Container ({container_size}, {container_status}, {container_type}) has no changes, skipping append.")
                    return True
                
                cursor.execute("SELECT CURRENT_TIMESTAMP")
                current_timestamp = cursor.fetchone()[0]
                
                cursor.execute(
                    f"UPDATE dbo.{table_name} SET end_time = ?, is_active = N'N' WHERE container_key = ?",
                    (current_timestamp, old_container_key)
                )
                
                cursor.execute(
                    f"""INSERT INTO dbo.{table_name} (container_size, container_status, container_type, start_time, end_time, is_active)
                       VALUES (?, ?, ?, ?, NULL, N'Y')""",
                    (container_size, container_status, container_type, current_timestamp)
                )
            else:
                cursor.execute(
                    f"""INSERT INTO dbo.{table_name} (container_size, container_status, container_type, start_time, end_time, is_active)
                       VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL, N'Y')""",
                    (container_size, container_status, container_type)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ContainerService] Error saving container: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

