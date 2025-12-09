import traceback
import json
from typing import Dict
from test.test_case.base_test import BaseTest
from features.user_management.user_service import UserService
from utils.db_helper import get_db_connection

class TestCase1UserPermissions(BaseTest):
    def __init__(self):
        super().__init__()
        self.test_actions = None
    
    def get_test_name(self) -> str:
        return "Test Case 1: Phân quyền tài khoản"
    
    def get_test_description(self) -> str:
        return "Kiểm tra các tài khoản có được phân quyền đúng trên UI không (ADMIN, EDITOR, VIEWER). Lưu vào bảng test_*"
    
    def run(self) -> Dict:
        self.steps = []
        
        try:
            self.log_step("Bước 1: Kiểm tra test actions", "info", "Đang đọc các thao tác user đã thực hiện")
            
            test_actions_str = self.test_actions
            
            if not test_actions_str:
                self.log_step("Bước 1: Kiểm tra test actions", "info", "Chưa có thao tác nào được ghi nhận. Test sẽ redirect về login page để user thực hiện các thao tác.")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Chưa có thao tác nào được ghi nhận. Vui lòng thực hiện các thao tác trên UI.",
                    "steps": self.steps,
                    "redirect_to_login": True
                }
            
            try:
                test_actions = json.loads(test_actions_str) if isinstance(test_actions_str, str) else test_actions_str
            except:
                test_actions = []
            
            if not test_actions or len(test_actions) == 0:
                self.log_step("Bước 1: Kiểm tra test actions", "info", "Chưa có thao tác nào được ghi nhận")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Chưa có thao tác nào được ghi nhận. Vui lòng thực hiện các thao tác trên UI.",
                    "steps": self.steps,
                    "redirect_to_login": True
                }
            
            self.log_step("Bước 1: Kiểm tra test actions", "success", f"Tìm thấy {len(test_actions)} thao tác", {"actions_count": len(test_actions)})
            
            self.log_step("Bước 2: Kết nối database", "info", "Đang kết nối database để kiểm tra dữ liệu trong test_users")
            conn = get_db_connection()
            if not conn:
                self.log_step("Bước 2: Kết nối database", "fail", "Không thể kết nối database")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Không thể kết nối database",
                    "steps": self.steps
                }
            
            self.log_step("Bước 2: Kết nối database", "success", "Đã kết nối database")
            
            self.log_step("Bước 3: Phân tích từng thao tác", "info", f"Đang phân tích {len(test_actions)} thao tác")
            
            all_passed = True
            action_results = []
            
            for idx, action in enumerate(test_actions, 1):
                action_type = action.get("type", "unknown")
                action_data = action.get("data", {})
                timestamp = action.get("timestamp", "")
                
                step_name = f"Bước 3.{idx}: Thao tác {action_type}"
                self.log_step(step_name, "info", f"Đang kiểm tra thao tác: {action_type}")
                
                action_result = {
                    "type": action_type,
                    "timestamp": timestamp,
                    "passed": False,
                    "message": "",
                    "details": {}
                }
                
                try:
                    if action_type == "register":
                        username = action_data.get("username", "")
                        role_name = action_data.get("role_name", "")
                        success = action_data.get("success", False)
                        error = action_data.get("error", "")
                        
                        if success:
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT u.user_name, r.role_name 
                                FROM dbo.test_users u
                                LEFT JOIN dbo.test_roles r ON u.role_key = r.role_key
                                WHERE LOWER(u.user_name) = LOWER(?)
                            """, (username,))
                            user_row = cursor.fetchone()
                            
                            if user_row:
                                db_username, db_role = user_row
                                if db_username.lower() == username.lower() and db_role == role_name:
                                    action_result["passed"] = True
                                    action_result["message"] = f"Đăng ký thành công: user {username} với role {role_name} đã được lưu vào test_users"
                                    action_result["details"] = {"username": username, "role": role_name, "saved_to_db": True}
                                    self.log_step(step_name, "success", action_result["message"])
                                else:
                                    action_result["passed"] = False
                                    action_result["message"] = f"Đăng ký không đúng: user {username} có role trong DB là {db_role}, không phải {role_name}"
                                    action_result["details"] = {"username": username, "expected_role": role_name, "actual_role": db_role}
                                    self.log_step(step_name, "fail", action_result["message"])
                                    all_passed = False
                            else:
                                action_result["passed"] = False
                                action_result["message"] = f"Đăng ký không thành công: user {username} không tìm thấy trong test_users"
                                action_result["details"] = {"username": username, "saved_to_db": False}
                                self.log_step(step_name, "fail", action_result["message"])
                                all_passed = False
                        else:
                            action_result["passed"] = True
                            action_result["message"] = f"Đăng ký thất bại (đúng như mong đợi): {error}"
                            action_result["details"] = {"username": username, "error": error, "expected_failure": True}
                            self.log_step(step_name, "success", action_result["message"])
                    
                    elif action_type == "login":
                        username = action_data.get("username", "")
                        success = action_data.get("success", False)
                        error = action_data.get("error", "")
                        
                        if success:
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT u.user_name, r.role_name 
                                FROM dbo.test_users u
                                LEFT JOIN dbo.test_roles r ON u.role_key = r.role_key
                                WHERE LOWER(u.user_name) = LOWER(?)
                            """, (username,))
                            user_row = cursor.fetchone()
                            
                            if user_row:
                                action_result["passed"] = True
                                action_result["message"] = f"Đăng nhập thành công: user {username} tồn tại trong test_users"
                                action_result["details"] = {"username": username, "role": user_row[1] or "N/A"}
                                self.log_step(step_name, "success", action_result["message"])
                            else:
                                action_result["passed"] = False
                                action_result["message"] = f"Đăng nhập không thành công: user {username} không tìm thấy trong test_users"
                                action_result["details"] = {"username": username}
                                self.log_step(step_name, "fail", action_result["message"])
                                all_passed = False
                        else:
                            action_result["passed"] = True
                            action_result["message"] = f"Đăng nhập thất bại (đúng như mong đợi): {error}"
                            action_result["details"] = {"username": username, "error": error, "expected_failure": True}
                            self.log_step(step_name, "success", action_result["message"])
                    
                    elif action_type == "update_user":
                        username = action_data.get("username", "")
                        success = action_data.get("success", False)
                        error = action_data.get("error", "")
                        updated_fields = action_data.get("updated_fields", {})
                        
                        if success:
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT first_name, middle_name, last_name, department_key, role_key
                                FROM dbo.test_users
                                WHERE LOWER(user_name) = LOWER(?)
                            """, (username,))
                            user_row = cursor.fetchone()
                            
                            if user_row:
                                db_first_name, db_middle_name, db_last_name, db_department_key, db_role_key = user_row
                                
                                checks = []
                                if "first_name" in updated_fields:
                                    checks.append(("first_name", updated_fields["first_name"], db_first_name))
                                if "middle_name" in updated_fields:
                                    checks.append(("middle_name", updated_fields["middle_name"], db_middle_name))
                                if "last_name" in updated_fields:
                                    checks.append(("last_name", updated_fields["last_name"], db_last_name))
                                if "department_key" in updated_fields:
                                    checks.append(("department_key", updated_fields["department_key"], db_department_key))
                                if "role_name" in updated_fields:
                                    cursor.execute("SELECT role_name FROM dbo.test_roles WHERE role_key = ?", (db_role_key,))
                                    role_row = cursor.fetchone()
                                    db_role_name = role_row[0] if role_row else None
                                    checks.append(("role_name", updated_fields["role_name"], db_role_name))
                                
                                all_fields_match = all(
                                    str(expected or "").strip() == str(actual or "").strip() 
                                    for _, expected, actual in checks
                                )
                                
                                if all_fields_match:
                                    action_result["passed"] = True
                                    action_result["message"] = f"Cập nhật thành công: tất cả các trường đã được cập nhật đúng trong test_users"
                                    action_result["details"] = {"username": username, "updated_fields": updated_fields}
                                    self.log_step(step_name, "success", action_result["message"])
                                else:
                                    action_result["passed"] = False
                                    mismatches = [f"{field}: expected={expected}, actual={actual}" for field, expected, actual in checks if str(expected or "").strip() != str(actual or "").strip()]
                                    action_result["message"] = f"Cập nhật không đúng: {', '.join(mismatches)}"
                                    action_result["details"] = {"username": username, "mismatches": mismatches}
                                    self.log_step(step_name, "fail", action_result["message"])
                                    all_passed = False
                            else:
                                action_result["passed"] = False
                                action_result["message"] = f"Cập nhật không thành công: user {username} không tìm thấy trong test_users"
                                action_result["details"] = {"username": username}
                                self.log_step(step_name, "fail", action_result["message"])
                                all_passed = False
                        else:
                            action_result["passed"] = True
                            action_result["message"] = f"Cập nhật thất bại (đúng như mong đợi): {error}"
                            action_result["details"] = {"username": username, "error": error, "expected_failure": True}
                            self.log_step(step_name, "success", action_result["message"])
                    
                    else:
                        action_result["passed"] = False
                        action_result["message"] = f"Loại thao tác không được hỗ trợ: {action_type}"
                        action_result["details"] = {"action_type": action_type}
                        self.log_step(step_name, "fail", action_result["message"])
                        all_passed = False
                
                except Exception as e:
                    action_result["passed"] = False
                    action_result["message"] = f"Lỗi khi kiểm tra thao tác: {str(e)}"
                    action_result["details"] = {"error": traceback.format_exc()}
                    self.log_step(step_name, "fail", action_result["message"])
                    all_passed = False
                
                action_results.append(action_result)
            
            conn.close()
            
            passed_count = sum(1 for r in action_results if r["passed"])
            failed_count = len(action_results) - passed_count
            
            if all_passed and len(action_results) > 0:
                self.log_step("Bước 3: Phân tích từng thao tác", "success", f"Tất cả {len(action_results)} thao tác đều PASS")
            else:
                self.log_step("Bước 3: Phân tích từng thao tác", "fail", f"Có {failed_count}/{len(action_results)} thao tác FAIL")
            
            return {
                "test_name": self.get_test_name(),
                "passed": all_passed and len(action_results) > 0,
                "message": "PASS" if (all_passed and len(action_results) > 0) else f"Có {failed_count} thao tác FAIL trong tổng số {len(action_results)} thao tác",
                "steps": self.steps,
                "details": {
                    "total_actions": len(action_results),
                    "passed_actions": passed_count,
                    "failed_actions": failed_count,
                    "action_results": action_results
                }
            }
        except Exception as e:
            self.log_step("Lỗi", "fail", f"Lỗi: {str(e)}", {"error": traceback.format_exc()})
            return {
                "test_name": self.get_test_name(),
                "passed": False,
                "message": f"Lỗi: {str(e)}",
                "steps": self.steps,
                "details": {"error": traceback.format_exc()}
            }
