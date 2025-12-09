from typing import Optional
from utils.db_helper import get_db_connection


class ContainerKeyService:
    
    def get_container_key(self, container_size: str, container_status: str, container_type: str, use_test_tables: bool = False) -> Optional[str]:
        if not container_size or not container_status or not container_type:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            table_name = "test_containers" if use_test_tables else "containers"
            print(f"[ContainerKeyService] use_test_tables={use_test_tables}, using table: {table_name}, looking for container: size={container_size}, status={container_status}, type={container_type}")
            cursor.execute(
                f"SELECT container_key FROM dbo.{table_name} WHERE container_size = ? AND container_status = ? AND container_type = ? AND is_active = N'Y'",
                (container_size, container_status, container_type)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"[ContainerKeyService] Error querying container_key: {e}")
            try:
                conn.close()
            except:
                pass
            return None

