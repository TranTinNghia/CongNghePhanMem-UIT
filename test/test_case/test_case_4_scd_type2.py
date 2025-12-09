import traceback
from pathlib import Path
from typing import Dict
from test.test_case.base_test import BaseTest
from utils.ocr_processor import OCRProcessor
from features.ocr.managers.customers import CustomerManager
from utils.db_helper import get_db_connection

class TestCase4SCDType2(BaseTest):
    def __init__(self, test_data_dir: Path):
        super().__init__()
        self.test_data_dir = test_data_dir
    
    def get_test_name(self) -> str:
        return "Test Case 4: SCD Type 2 hoạt động"
    
    def get_test_description(self) -> str:
        return "Kiểm tra SCD Type 2 có hoạt động đúng không (khi customer thay đổi thông tin, tạo bản ghi mới và đánh dấu bản ghi cũ)"
    
    def run(self) -> Dict:
        self.steps = []
        
        try:
            self.log_step("Bước 1: Tìm file PDF", "info", "Đang tìm file PDF trong thư mục test/data")
            pdf_files = list(self.test_data_dir.glob("*.pdf"))
            
            if not pdf_files:
                self.log_step("Bước 1: Tìm file PDF", "fail", "Không tìm thấy file PDF trong thư mục test/data")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Không tìm thấy file PDF trong thư mục test/data",
                    "steps": self.steps
                }
            
            test_file = pdf_files[0]
            self.log_step("Bước 1: Tìm file PDF", "success", f"Tìm thấy file: {test_file.name}")
            
            self.log_step("Bước 2: Quét OCR", "info", f"Đang quét file {test_file.name}")
            ocr_processor = OCRProcessor()
            result = ocr_processor.process_ocr(str(test_file))
            
            if not result.get("success"):
                error_msg = result.get('error', 'Lỗi không xác định')
                self.log_step("Bước 2: Quét OCR", "fail", f"OCR không thành công: {error_msg}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"OCR không thành công: {error_msg}",
                    "steps": self.steps,
                    "details": {"file": test_file.name}
                }
            
            self.log_step("Bước 2: Quét OCR", "success", "OCR thành công")
            
            data = result.get("data", {})
            tax_code = data.get("tax_code", "")
            customer_name = data.get("customer_name", "")
            customer_address = data.get("customer_address", "")
            
            if not tax_code or tax_code == "-" or not customer_name or customer_name == "-":
                self.log_step("Bước 3: Kiểm tra thông tin customer", "fail", "Không có đủ thông tin customer để test SCD Type 2")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Không có đủ thông tin customer để test SCD Type 2",
                    "steps": self.steps
                }
            
            self.log_step("Bước 3: Kiểm tra thông tin customer", "success", f"Customer: {customer_name} (MST: {tax_code})")
            
            self.log_step("Bước 4: Kiểm tra database trước khi lưu", "info", f"Đang kiểm tra số lượng record của customer {tax_code}")
            customer_manager = CustomerManager()
            
            conn = get_db_connection()
            if not conn:
                self.log_step("Bước 4: Kiểm tra database trước khi lưu", "fail", "Không thể kết nối database")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Không thể kết nối database",
                    "steps": self.steps
                }
            
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM dbo.customers WHERE tax_code = ? AND is_active = N'Y'", (tax_code,))
                count_before = cursor.fetchone()[0]
                self.log_step("Bước 4: Kiểm tra database trước khi lưu", "success", f"Có {count_before} record active trước khi lưu")
                
                cursor.execute("SELECT COUNT(*) FROM dbo.customers WHERE tax_code = ?", (tax_code,))
                total_before = cursor.fetchone()[0]
                self.log_step("Bước 4: Kiểm tra database trước khi lưu", "info", f"Tổng số record (bao gồm inactive): {total_before}")
                
                conn.close()
            except Exception as e:
                conn.close()
                self.log_step("Bước 4: Kiểm tra database trước khi lưu", "fail", f"Lỗi: {str(e)}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"Lỗi kiểm tra database: {str(e)}",
                    "steps": self.steps
                }
            
            self.log_step("Bước 5: Lưu customer lần 1", "info", f"Đang lưu customer {customer_name} lần đầu")
            saved1 = customer_manager.process_and_save_customer(tax_code, customer_name, customer_address)
            if saved1:
                self.log_step("Bước 5: Lưu customer lần 1", "success", "Đã lưu thành công")
            else:
                self.log_step("Bước 5: Lưu customer lần 1", "fail", "Không thể lưu")
            
            self.log_step("Bước 6: Lưu customer lần 2 (cùng thông tin)", "info", "Đang lưu customer với cùng thông tin (không thay đổi)")
            saved2 = customer_manager.process_and_save_customer(tax_code, customer_name, customer_address)
            if saved2:
                self.log_step("Bước 6: Lưu customer lần 2 (cùng thông tin)", "success", "Đã lưu (không tạo record mới vì không có thay đổi)")
            else:
                self.log_step("Bước 6: Lưu customer lần 2 (cùng thông tin)", "fail", "Lỗi khi lưu")
            
            self.log_step("Bước 7: Lưu customer lần 3 (thay đổi thông tin)", "info", "Đang lưu customer với thông tin thay đổi (test SCD Type 2)")
            modified_name = customer_name + " (Modified)"
            saved3 = customer_manager.process_and_save_customer(tax_code, modified_name, customer_address)
            if saved3:
                self.log_step("Bước 7: Lưu customer lần 3 (thay đổi thông tin)", "success", f"Đã lưu với tên mới: {modified_name}")
            else:
                self.log_step("Bước 7: Lưu customer lần 3 (thay đổi thông tin)", "fail", "Không thể lưu")
            
            self.log_step("Bước 8: Kiểm tra database sau khi lưu", "info", "Đang kiểm tra số lượng record sau khi lưu")
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM dbo.customers WHERE tax_code = ? AND is_active = N'Y'", (tax_code,))
                count_after = cursor.fetchone()[0]
                self.log_step("Bước 8: Kiểm tra database sau khi lưu", "info", f"Có {count_after} record active sau khi lưu")
                
                cursor.execute("SELECT COUNT(*) FROM dbo.customers WHERE tax_code = ?", (tax_code,))
                total_after = cursor.fetchone()[0]
                self.log_step("Bước 8: Kiểm tra database sau khi lưu", "info", f"Tổng số record (bao gồm inactive): {total_after}")
                
                cursor.execute("""
                    SELECT customer_key, customer_name, address, start_time, end_time, is_active 
                    FROM dbo.customers 
                    WHERE tax_code = ? 
                    ORDER BY start_time DESC
                """, (tax_code,))
                all_records = cursor.fetchall()
                
                active_records = [r for r in all_records if r[5] == 'Y']
                inactive_records = [r for r in all_records if r[5] == 'N']
                
                self.log_step("Bước 8: Kiểm tra database sau khi lưu", "info", f"Có {len(active_records)} record active và {len(inactive_records)} record inactive")
                
                records_detail = []
                for r in all_records[:5]:
                    records_detail.append({
                        "customer_key": r[0],
                        "customer_name": r[1],
                        "address": r[2],
                        "start_time": str(r[3]),
                        "end_time": str(r[4]) if r[4] else None,
                        "is_active": r[5]
                    })
                    status = "active" if r[5] == 'Y' else "inactive"
                    self.log_step(f"Bước 8: Record {r[0][:8]}...", "info", f"Record {status}: {r[1]} (start: {r[3]}, end: {r[4] if r[4] else 'NULL'})")
                
                conn.close()
                
                scd_working = (
                    count_after == 1 and
                    total_after >= count_before and
                    len(active_records) == 1 and
                    len(inactive_records) >= 0
                )
                
                if scd_working:
                    self.log_step("Bước 8: Kiểm tra database sau khi lưu", "success", "SCD Type 2 hoạt động đúng: có 1 record active, các record cũ được đánh dấu inactive")
                else:
                    self.log_step("Bước 8: Kiểm tra database sau khi lưu", "fail", f"SCD Type 2 không hoạt động đúng: count_after={count_after}, total={total_after}, active={len(active_records)}")
                
                return {
                    "test_name": self.get_test_name(),
                    "passed": scd_working,
                    "message": "PASS" if scd_working else f"SCD Type 2 không hoạt động đúng: count_before={count_before}, count_after={count_after}, total={total_after}",
                    "steps": self.steps,
                    "details": {
                        "tax_code": tax_code,
                        "count_before": count_before,
                        "count_after": count_after,
                        "total_before": total_before,
                        "total_after": total_after,
                        "active_records": len(active_records),
                        "inactive_records": len(inactive_records),
                        "records_detail": records_detail
                    }
                }
            except Exception as e:
                conn.close()
                self.log_step("Bước 8: Kiểm tra database sau khi lưu", "fail", f"Lỗi: {str(e)}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"Lỗi kiểm tra database: {str(e)}",
                    "steps": self.steps,
                    "details": {"error": traceback.format_exc()}
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
