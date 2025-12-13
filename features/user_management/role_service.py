from typing import Optional, List, Dict
from utils.db_helper import get_db_connection
class RoleService:
    def get_role_key_by_name(self, role_name: str) -> Optional[str]:
        if not role_name:
            return None
        role_name = role_name.strip().upper()
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role_key FROM dbo.roles WHERE UPPER(role_name) = ?",
                (role_name,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"[RoleService] Error getting role_key: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    def get_all_roles(self) -> List[Dict[str, str]]:
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role_key, role_name FROM dbo.roles ORDER BY role_name"
            )
            results = cursor.fetchall()
            conn.close()
            roles = []
            for row in results:
                roles.append({
                    "role_key": row[0],
                    "role_name": row[1]
                })
            return roles
        except Exception as e:
            print(f"[RoleService] Error getting all roles: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    def get_roles_for_registration(self) -> List[Dict[str, str]]:
        allowed_roles = ["VIEWER", "EDITOR"]
        all_roles = self.get_all_roles()
        return [
            role for role in all_roles
            if role["role_name"].upper() in allowed_roles
        ]
