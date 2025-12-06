from typing import Optional, Dict
from datetime import datetime
from calendar import monthrange
from utils.db_helper import get_db_connection


class CustomerSearchService:
    
    def _format_province_name(self, province_name: str) -> str:
        if not province_name:
            return ""
        
        province_name = province_name.strip()
        
        city_names = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Huế"]
        
        if province_name in city_names:
            return f"Thành Phố {province_name}"
        else:
            return f"Tỉnh {province_name}"
    
    def get_monthly_revenue(self, tax_code: str) -> Optional[Dict]:
        if not tax_code:
            return None
        
        tax_code = tax_code.strip()
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            start_year = 2024
            start_month = 1
            
            revenue_by_month = {}
            container_count_by_month = {}
            
            year = start_year
            month = start_month
            while year < current_year or (year == current_year and month <= current_month):
                month_key = f"{month}/{year}"
                revenue_by_month[month_key] = 0
                container_count_by_month[month_key] = 0
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            
            start_date = datetime(start_year, start_month, 1)
            last_day = monthrange(current_year, current_month)[1]
            end_date = datetime(current_year, current_month, last_day)
            
            cursor.execute(
                """
                SELECT 
                    YEAR(r.receipt_date) as year,
                    MONTH(r.receipt_date) as month,
                    SUM(l.amount) as total_amount,
                    COUNT(DISTINCT l.container_number) as container_count
                FROM dbo.lines l
                INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                WHERE c.tax_code = ? 
                    AND c.is_active = N'Y'
                    AND r.receipt_date >= ?
                    AND r.receipt_date <= ?
                GROUP BY YEAR(r.receipt_date), MONTH(r.receipt_date)
                ORDER BY YEAR(r.receipt_date), MONTH(r.receipt_date)
                """,
                (tax_code, start_date, end_date)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            for row in results:
                year = row[0]
                month = row[1]
                total_amount = row[2] or 0
                container_count = row[3] or 0
                month_key = f"{month}/{year}"
                if month_key in revenue_by_month:
                    revenue_by_month[month_key] = int(total_amount)
                    container_count_by_month[month_key] = int(container_count)
            
            return {
                "revenue": revenue_by_month,
                "container_count": container_count_by_month
            }
        except Exception as e:
            print(f"[CustomerSearchService] Error getting monthly revenue: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def search_by_tax_code(self, tax_code: str) -> Optional[Dict]:
        if not tax_code:
            return None
        
        tax_code = tax_code.strip()
        
        if not tax_code.isdigit():
            return None
        
        if len(tax_code) > 11:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT c.customer_name, c.address, p.new_province
                   FROM dbo.customers c
                   LEFT JOIN dbo.provinces p ON c.province_key = p.province_key
                   WHERE c.tax_code = ? AND c.is_active = N'Y' AND p.is_active = N'Y'""",
                (tax_code,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                new_province = result[2] or ""
                formatted_province = self._format_province_name(new_province) if new_province else ""
                
                monthly_revenue = self.get_monthly_revenue(tax_code)
                
                return {
                    "customer_name": result[0] or "",
                    "address": result[1] or "",
                    "new_province": formatted_province,
                    "monthly_revenue": monthly_revenue or {}
                }
            return None
        except Exception as e:
            print(f"[CustomerSearchService] Error searching customer: {e}")
            try:
                conn.close()
            except:
                pass
            return None

