from typing import Optional
from utils.db_helper import get_db_connection


class ContainerKeyService:
    
    def get_container_key(self, container_size: str, container_status: str, container_type: str) -> Optional[str]:
        if not container_size or not container_status or not container_type:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT container_key FROM dbo.containers WHERE container_size = ? AND container_status = ? AND container_type = ? AND is_active = N'Y'",
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

