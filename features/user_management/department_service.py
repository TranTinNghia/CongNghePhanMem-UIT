from typing import Optional, List, Dict
from utils.db_helper import get_db_connection
class DepartmentService:
    def get_department_key_by_name(self, department_name: str) -> Optional[str]:
        if not department_name:
            return None
        department_name = department_name.strip()
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT department_key FROM dbo.departments WHERE department = ?",
                (department_name,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"[DepartmentService] Error getting department_key: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    def get_all_departments(self) -> List[Dict[str, str]]:
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT department_key, department FROM dbo.departments ORDER BY department"
            )
            results = cursor.fetchall()
            conn.close()
            departments = []
            for row in results:
                departments.append({
                    "department_key": row[0],
                    "department": row[1]
                })
            return departments
        except Exception as e:
            print(f"[DepartmentService] Error getting all departments: {e}")
            try:
                conn.close()
            except:
                pass
            return []
