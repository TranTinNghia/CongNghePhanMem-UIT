from typing import Optional
from utils.db_helper import get_db_connection

class CustomerCountService:
    
    def get_active_customer_count(self) -> Optional[int]:
        """
        Lấy số lượng khách hàng đang hoạt động (is_active = "Y")
        Returns:
            Số lượng khách hàng hoặc None nếu có lỗi
        """
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM dbo.customers WHERE is_active = N'Y'"
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return 0
        except Exception as e:
            print(f"[CustomerCountService] Error counting customers: {e}")
            try:
                conn.close()
            except:
                pass
            return None

