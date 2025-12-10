from typing import Optional
from utils.db_helper import get_db_connection

class DocumentCountService:
    
    def get_document_count(self) -> Optional[int]:
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            # Đếm tổng số receipts trong database
            cursor.execute("SELECT COUNT(*) FROM dbo.receipts")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return 0
        except Exception as e:
            print(f"[DocumentCountService] Error counting documents: {e}")
            try:
                conn.close()
            except:
                pass
            return None

