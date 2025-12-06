from typing import Optional
from utils.db_helper import get_db_connection

class UserService:
    
    def is_admin(self, username: str) -> bool:
        if not username:
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT u.user_name 
                   FROM dbo.users u
                   INNER JOIN dbo.roles r ON u.role_key = r.role_key
                   WHERE LOWER(u.user_name) = LOWER(?) AND UPPER(r.role_name) = 'ADMIN'""",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            print(f"[UserService] Error checking admin: {e}")
            try:
                conn.close()
            except:
                pass
            return False
    
    def get_user_role(self, username: str) -> Optional[str]:
        if not username:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT r.role_name 
                   FROM dbo.users u
                   INNER JOIN dbo.roles r ON u.role_key = r.role_key
                   WHERE LOWER(u.user_name) = LOWER(?)""",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"[UserService] Error getting user role: {e}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def get_all_users(self) -> list:
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT u.user_name, u.email, u.phone_number, u.first_name, u.middle_name, u.last_name, r.role_name, r.role_key, d.department, d.department_key
                   FROM dbo.users u
                   LEFT JOIN dbo.roles r ON u.role_key = r.role_key
                   LEFT JOIN dbo.departments d ON u.department_key = d.department_key
                   ORDER BY u.user_name"""
            )
            results = cursor.fetchall()
            conn.close()
            
            users = []
            for row in results:
                users.append({
                    "username": row[0],
                    "email": row[1] or "",
                    "phone_number": row[2] or "",
                    "first_name": row[3] or "",
                    "middle_name": row[4] or "",
                    "last_name": row[5] or "",
                    "role_name": row[6] or "N/A",
                    "role_key": row[7] or "",
                    "department": row[8] or "",
                    "department_key": row[9] or ""
                })
            return users
        except Exception as e:
            print(f"[UserService] Error getting all users: {e}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def has_any_users(self) -> bool:
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dbo.users")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"[UserService] Error checking users: {e}")
            try:
                conn.close()
            except:
                pass
            return False
    
    def assign_role(self, username: str, role_key: str) -> bool:
        if not username or not role_key:
            print(f"[UserService] assign_role: Missing username or role_key. username={username}, role_key={role_key}")
            return False
        
        conn = get_db_connection()
        if not conn:
            print(f"[UserService] assign_role: Cannot get database connection")
            return False
        
        try:
            cursor = conn.cursor()
            # Kiểm tra xem user có tồn tại không
            cursor.execute(
                "SELECT user_name FROM dbo.users WHERE LOWER(user_name) = LOWER(?)",
                (username,)
            )
            user_exists = cursor.fetchone()
            if not user_exists:
                print(f"[UserService] assign_role: User '{username}' does not exist")
                conn.close()
                return False
            
            # Kiểm tra xem role_key có tồn tại không
            cursor.execute(
                "SELECT role_key FROM dbo.roles WHERE role_key = ?",
                (role_key,)
            )
            role_exists = cursor.fetchone()
            if not role_exists:
                print(f"[UserService] assign_role: Role key '{role_key}' does not exist")
                conn.close()
                return False
            
            # Cập nhật role
            cursor.execute(
                "UPDATE dbo.users SET role_key = ? WHERE LOWER(user_name) = LOWER(?)",
                (role_key, username)
            )
            rows_affected = cursor.rowcount
            print(f"[UserService] assign_role: Updated {rows_affected} row(s) for user '{username}' with role_key '{role_key}'")
            
            if rows_affected == 0:
                print(f"[UserService] assign_role: No rows updated for user '{username}'")
                conn.rollback()
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[UserService] Error assigning role: {e}")
            import traceback
            traceback.print_exc()
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False
    
    def update_user_info(self, username: str, first_name: Optional[str], middle_name: Optional[str], last_name: Optional[str], department_key: Optional[str]) -> bool:
        if not username:
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            update_fields = []
            update_values = []
            
            if first_name is not None:
                update_fields.append("first_name = ?")
                update_values.append(first_name)
            
            if middle_name is not None:
                update_fields.append("middle_name = ?")
                update_values.append(middle_name)
            
            if last_name is not None:
                update_fields.append("last_name = ?")
                update_values.append(last_name)
            
            if department_key is not None:
                if department_key == "":
                    update_fields.append("department_key = NULL")
                else:
                    update_fields.append("department_key = ?")
                    update_values.append(department_key)
            
            if update_fields:
                update_values.append(username)
                cursor.execute(
                    f"UPDATE dbo.users SET {', '.join(update_fields)} WHERE LOWER(user_name) = LOWER(?)",
                    tuple(update_values)
                )
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"[UserService] Error updating user info: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

