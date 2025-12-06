from datetime import datetime
from typing import Optional, List, Dict
from utils.db_helper import get_db_connection

class DashboardReportService:
    
    def get_total_customers(self) -> Optional[int]:
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
            print(f"[DashboardReportService] Error getting total customers: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def get_customers_list(self) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT DISTINCT 
                    c.customer_key,
                    c.tax_code,
                    c.customer_name
                FROM dbo.customers c
                WHERE c.is_active = N'Y'
                ORDER BY c.customer_name"""
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "customer_key": row[0],
                    "tax_code": row[1],
                    "customer_name": row[2]
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting customers list: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_months_list(self) -> List[str]:
        months = []
        start_date = datetime(2024, 1, 1)
        current_date = datetime.now()
        
        current = start_date
        while current <= current_date:
            months.append(current.strftime('%m/%Y'))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    def get_customer_monthly_revenue(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                placeholders = ','.join(['?' for _ in customer_keys])
                where_clauses.append(f"c.customer_key IN ({placeholders})")
                params.extend(customer_keys)
            
            if month_years and len(month_years) > 0:
                placeholders = ','.join(['?' for _ in month_years])
                where_clauses.append(f"FORMAT(r.receipt_date, 'MM/yyyy') IN ({placeholders})")
                params.extend(month_years)
            
            where_sql = " AND ".join(where_clauses)
            
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT 
                    c.customer_key,
                    c.tax_code,
                    c.customer_name,
                    FORMAT(r.receipt_date, 'MM/yyyy') AS month_year,
                    SUM(l.amount) AS total_revenue,
                    COUNT(DISTINCT l.container_number) AS total_containers
                FROM dbo.lines l
                INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                WHERE {where_sql}
                GROUP BY c.customer_key, c.tax_code, c.customer_name, FORMAT(r.receipt_date, 'MM/yyyy')
                ORDER BY c.customer_name, month_year""",
                tuple(params)
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "customer_key": row[0],
                    "tax_code": row[1],
                    "customer_name": row[2],
                    "month_year": row[3],
                    "total_revenue": float(row[4]) if row[4] else 0,
                    "total_containers": row[5]
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting customer monthly revenue: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_monthly_container_usage(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                # Clean và filter customer_keys
                cleaned_customer_keys = [k.strip() for k in customer_keys if k and k.strip()]
                if len(cleaned_customer_keys) == 0:
                    print(f"[get_monthly_container_usage] No valid customer_keys after cleaning")
                else:
                    # Luôn dùng IN, kể cả khi chỉ có 1 giá trị (để tránh vấn đề với pyodbc)
                    placeholders = ','.join(['?' for _ in cleaned_customer_keys])
                    where_clauses.append(f"c.customer_key IN ({placeholders})")
                    params.extend(cleaned_customer_keys)
                    print(f"[get_monthly_container_usage] Filtering by {len(cleaned_customer_keys)} customer_keys: {cleaned_customer_keys}")
            else:
                print(f"[get_monthly_container_usage] No customer_keys filter applied")
            
            if month_years and len(month_years) > 0:
                placeholders = ','.join(['?' for _ in month_years])
                where_clauses.append(f"FORMAT(r.receipt_date, 'MM/yyyy') IN ({placeholders})")
                params.extend(month_years)
                print(f"[get_monthly_container_usage] Filtering by month_years: {month_years}")
            
            where_sql = " AND ".join(where_clauses)
            print(f"[get_monthly_container_usage] WHERE clause: {where_sql}")
            print(f"[get_monthly_container_usage] Params: {params}, type: {type(params)}")
            print(f"[get_monthly_container_usage] Params tuple: {tuple(params) if params else None}")
            
            cursor = conn.cursor()
            sql_query = f"""SELECT 
                    FORMAT(r.receipt_date, 'MM/yyyy') AS month_year,
                    cont.container_size,
                    COUNT(*) AS total_count
                FROM dbo.lines l
                INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                INNER JOIN dbo.services s ON l.service_key = s.service_key
                INNER JOIN dbo.containers cont ON s.container_key = cont.container_key
                WHERE {where_sql}
                    AND s.is_active = N'Y'
                    AND cont.is_active = N'Y'
                GROUP BY FORMAT(r.receipt_date, 'MM/yyyy'), cont.container_size
                ORDER BY month_year, cont.container_size"""
            
            print(f"[get_monthly_container_usage] SQL Query: {sql_query}")
            print(f"[get_monthly_container_usage] Executing with params: {tuple(params) if params else ()}")
            
            cursor.execute(sql_query, tuple(params) if params else ())
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "month_year": row[0],
                    "container_size": row[1],
                    "total_count": row[2]
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting monthly container usage: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_monthly_container_type_usage(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                # Clean và filter customer_keys, luôn dùng IN
                cleaned_customer_keys = [k.strip() for k in customer_keys if k and k.strip()]
                if len(cleaned_customer_keys) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_customer_keys])
                    where_clauses.append(f"c.customer_key IN ({placeholders})")
                    params.extend(cleaned_customer_keys)
            
            if month_years and len(month_years) > 0:
                # Clean và filter month_years, luôn dùng IN
                cleaned_month_years = [m.strip() for m in month_years if m and m.strip()]
                if len(cleaned_month_years) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_month_years])
                    where_clauses.append(f"FORMAT(r.receipt_date, 'MM/yyyy') IN ({placeholders})")
                    params.extend(cleaned_month_years)
            
            where_sql = " AND ".join(where_clauses)
            
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT 
                    FORMAT(r.receipt_date, 'MM/yyyy') AS month_year,
                    cont.container_type,
                    COUNT(*) AS total_count
                FROM dbo.lines l
                INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                INNER JOIN dbo.services s ON l.service_key = s.service_key
                INNER JOIN dbo.containers cont ON s.container_key = cont.container_key
                WHERE {where_sql}
                    AND s.is_active = N'Y'
                    AND cont.is_active = N'Y'
                    AND cont.container_type IS NOT NULL
                GROUP BY FORMAT(r.receipt_date, 'MM/yyyy'), cont.container_type
                ORDER BY month_year, cont.container_type""",
                tuple(params)
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "month_year": row[0],
                    "container_type": row[1] or "N/A",
                    "total_count": row[2]
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting monthly container type usage: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_customer_container_usage(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                placeholders = ','.join(['?' for _ in customer_keys])
                where_clauses.append(f"c.customer_key IN ({placeholders})")
                params.extend(customer_keys)
            
            if month_years and len(month_years) > 0:
                placeholders = ','.join(['?' for _ in month_years])
                where_clauses.append(f"FORMAT(r.receipt_date, 'MM/yyyy') IN ({placeholders})")
                params.extend(month_years)
            
            where_sql = " AND ".join(where_clauses)
            
            cursor = conn.cursor()
            cursor.execute(
                f"""WITH ContainerUsage AS (
                    SELECT 
                        c.tax_code,
                        c.customer_name,
                        FORMAT(r.receipt_date, 'MM/yyyy') AS month_year,
                        cont.container_type,
                        cont.container_size,
                        COUNT(*) AS usage_count
                    FROM dbo.lines l
                    INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                    INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                    INNER JOIN dbo.services s ON l.service_key = s.service_key
                    INNER JOIN dbo.containers cont ON s.container_key = cont.container_key
                    WHERE {where_sql}
                        AND s.is_active = N'Y'
                        AND cont.is_active = N'Y'
                    GROUP BY c.tax_code, c.customer_name, FORMAT(r.receipt_date, 'MM/yyyy'), 
                             cont.container_type, cont.container_size
                ),
                RankedUsage AS (
                    SELECT 
                        tax_code,
                        customer_name,
                        month_year,
                        container_type,
                        container_size,
                        usage_count,
                        ROW_NUMBER() OVER (PARTITION BY tax_code, customer_name, month_year ORDER BY usage_count DESC) AS rn_max,
                        ROW_NUMBER() OVER (PARTITION BY tax_code, customer_name, month_year ORDER BY usage_count ASC) AS rn_min
                    FROM ContainerUsage
                )
                SELECT 
                    tax_code,
                    customer_name,
                    month_year,
                    MAX(CASE WHEN rn_max = 1 THEN container_type END) AS most_used_type,
                    MAX(CASE WHEN rn_max = 1 THEN container_size END) AS most_used_size,
                    MAX(CASE WHEN rn_min = 1 THEN container_type END) AS least_used_type,
                    MAX(CASE WHEN rn_min = 1 THEN container_size END) AS least_used_size
                FROM RankedUsage
                GROUP BY tax_code, customer_name, month_year
                ORDER BY customer_name, month_year""",
                tuple(params)
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "tax_code": row[0],
                    "customer_name": row[1],
                    "month_year": row[2],
                    "most_used_type": row[3] or "N/A",
                    "most_used_size": row[4] or "N/A",
                    "least_used_type": row[5] or "N/A",
                    "least_used_size": row[6] or "N/A"
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting customer container usage: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_customers_by_province(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                # Clean và filter customer_keys, luôn dùng IN
                cleaned_customer_keys = [k.strip() for k in customer_keys if k and k.strip()]
                if len(cleaned_customer_keys) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_customer_keys])
                    where_clauses.append(f"c.customer_key IN ({placeholders})")
                    params.extend(cleaned_customer_keys)
            
            if month_years and len(month_years) > 0:
                # Clean và filter month_years, luôn dùng IN
                cleaned_month_years = [m.strip() for m in month_years if m and m.strip()]
                if len(cleaned_month_years) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_month_years])
                    where_clauses.append(f"EXISTS (SELECT 1 FROM dbo.receipts r2 INNER JOIN dbo.lines l2 ON r2.receipt_key = l2.receipt_key WHERE r2.customer_key = c.customer_key AND FORMAT(r2.receipt_date, 'MM/yyyy') IN ({placeholders}))")
                    params.extend(cleaned_month_years)
            
            where_sql = " AND ".join(where_clauses)
            
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT 
                    p.new_province,
                    COUNT(DISTINCT c.customer_key) AS customer_count
                FROM dbo.customers c
                INNER JOIN dbo.provinces p ON c.province_key = p.province_key
                WHERE {where_sql}
                    AND p.is_active = N'Y'
                GROUP BY p.new_province
                ORDER BY customer_count DESC""",
                tuple(params)
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "province": row[0] or "N/A",
                    "customer_count": row[1]
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting customers by province: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_revenue_by_province(self, customer_keys: Optional[List[str]] = None, month_years: Optional[List[str]] = None) -> List[Dict]:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            where_clauses = ["c.is_active = N'Y'"]
            params = []
            
            if customer_keys and len(customer_keys) > 0:
                # Clean và filter customer_keys, luôn dùng IN
                cleaned_customer_keys = [k.strip() for k in customer_keys if k and k.strip()]
                if len(cleaned_customer_keys) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_customer_keys])
                    where_clauses.append(f"c.customer_key IN ({placeholders})")
                    params.extend(cleaned_customer_keys)
            
            if month_years and len(month_years) > 0:
                # Clean và filter month_years, luôn dùng IN
                cleaned_month_years = [m.strip() for m in month_years if m and m.strip()]
                if len(cleaned_month_years) > 0:
                    placeholders = ','.join(['?' for _ in cleaned_month_years])
                    where_clauses.append(f"FORMAT(r.receipt_date, 'MM/yyyy') IN ({placeholders})")
                    params.extend(cleaned_month_years)
            
            where_sql = " AND ".join(where_clauses)
            
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT 
                    p.new_province,
                    SUM(l.amount) AS total_revenue
                FROM dbo.lines l
                INNER JOIN dbo.receipts r ON l.receipt_key = r.receipt_key
                INNER JOIN dbo.customers c ON r.customer_key = c.customer_key
                INNER JOIN dbo.provinces p ON c.province_key = p.province_key
                WHERE {where_sql}
                    AND p.is_active = N'Y'
                GROUP BY p.new_province
                ORDER BY total_revenue DESC""",
                tuple(params)
            )
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for row in results:
                data.append({
                    "province": row[0] or "N/A",
                    "total_revenue": float(row[1]) if row[1] else 0
                })
            return data
        except Exception as e:
            print(f"[DashboardReportService] Error getting revenue by province: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_data_version(self) -> Optional[str]:
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT 
                    (SELECT ISNULL(MAX(DATEDIFF_BIG(SECOND, '1970-01-01', start_time)), 0) FROM dbo.customers WHERE is_active = N'Y') AS max_customer_time,
                    (SELECT ISNULL(MAX(DATEDIFF_BIG(SECOND, '1970-01-01', receipt_date)), 0) FROM dbo.receipts) AS max_receipt_time,
                    (SELECT ISNULL(COUNT(*), 0) FROM dbo.lines) AS line_count"""
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                version = f"{result[0]}_{result[1]}_{result[2]}"
                return version
            return "0_0_0"
        except Exception as e:
            print(f"[DashboardReportService] Error getting data version: {e}")
            try:
                conn.close()
            except:
                pass
            return None
