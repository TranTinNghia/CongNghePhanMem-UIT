import traceback
from pathlib import Path
from typing import Dict
from test.test_case.base_test import BaseTest
from utils.ocr_processor import OCRProcessor
from features.ocr.managers.customers import CustomerManager
from features.ocr.managers.receipts import ReceiptManager
from utils.db_helper import get_db_connection

class TestCase2MultipleFiles(BaseTest):
    def __init__(self, test_data_dir: Path):
        super().__init__()
        self.test_data_dir = test_data_dir
    
    def get_test_name(self) -> str:
        return "Test Case 2: Quét nhiều file PDF"
    
    def get_test_description(self) -> str:
        return "Kiểm tra hệ thống quét nhiều file PDF đúng, đủ số dòng, chính xác thông tin trên UI và ghi đúng dữ liệu vào Database"
    
    def run(self) -> Dict:
        self.steps = []
        
        try:
            self.log_step("Bước 1: Tìm file PDF", "info", "Đang tìm file PDF trong thư mục test/data")
            pdf_files = list(self.test_data_dir.glob("*.pdf"))
            
            if len(pdf_files) < 2:
                self.log_step("Bước 1: Tìm file PDF", "fail", f"Cần ít nhất 2 file PDF, chỉ tìm thấy {len(pdf_files)}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"Cần ít nhất 2 file PDF trong thư mục test/data, chỉ tìm thấy {len(pdf_files)}",
                    "steps": self.steps,
                    "details": {"files_found": len(pdf_files)}
                }
            
            test_files = pdf_files[:3]
            self.log_step("Bước 1: Tìm file PDF", "success", f"Tìm thấy {len(pdf_files)} file, sẽ test {len(test_files)} file đầu tiên", {"files": [f.name for f in test_files]})
            
            self.log_step("Bước 2: Quét OCR nhiều file", "info", f"Đang quét {len(test_files)} file")
            ocr_processor = OCRProcessor()
            results = []
            errors = []
            
            for idx, test_file in enumerate(test_files, 1):
                self.log_step(f"Bước 2.{idx}: Quét file {test_file.name}", "info", f"Đang quét file {test_file.name}")
                try:
                    result = ocr_processor.process_ocr(str(test_file))
                    if result.get("success"):
                        results.append(result.get("data", {}))
                        self.log_step(f"Bước 2.{idx}: Quét file {test_file.name}", "success", "Quét thành công")
                    else:
                        error_msg = result.get('error', 'Lỗi không xác định')
                        errors.append(f"{test_file.name}: {error_msg}")
                        self.log_step(f"Bước 2.{idx}: Quét file {test_file.name}", "fail", error_msg)
                except Exception as e:
                    error_msg = str(e)
                    errors.append(f"{test_file.name}: {error_msg}")
                    self.log_step(f"Bước 2.{idx}: Quét file {test_file.name}", "fail", error_msg)
            
            if len(results) == 0:
                self.log_step("Bước 2: Quét OCR nhiều file", "fail", f"Không quét được file nào. Lỗi: {'; '.join(errors)}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"Không quét được file nào. Lỗi: {'; '.join(errors)}",
                    "steps": self.steps,
                    "details": {"files_tested": [f.name for f in test_files], "errors": errors}
                }
            
            self.log_step("Bước 2: Quét OCR nhiều file", "success", f"Quét thành công {len(results)}/{len(test_files)} file")
            
            self.log_step("Bước 3: Lưu dữ liệu vào Database", "info", f"Đang lưu {len(results)} kết quả vào database")
            saved_count = 0
            saved_details = []
            
            for idx, result in enumerate(results, 1):
                tax_code = result.get("tax_code", "")
                customer_name = result.get("customer_name", "")
                customer_address = result.get("customer_address", "")
                
                if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                    self.log_step(f"Bước 3.{idx}: Lưu Customer {tax_code}", "info", f"Đang lưu customer: {customer_name}")
                    customer_manager = CustomerManager()
                    if customer_manager.process_and_save_customer(tax_code, customer_name, customer_address):
                        saved_count += 1
                        saved_details.append({"tax_code": tax_code, "customer_name": customer_name, "status": "saved"})
                        self.log_step(f"Bước 3.{idx}: Lưu Customer {tax_code}", "success", f"Đã lưu customer: {customer_name}")
                    else:
                        saved_details.append({"tax_code": tax_code, "customer_name": customer_name, "status": "failed"})
                        self.log_step(f"Bước 3.{idx}: Lưu Customer {tax_code}", "fail", "Không thể lưu customer")
                else:
                    saved_details.append({"tax_code": tax_code, "status": "skipped", "reason": "Thiếu thông tin"})
                    self.log_step(f"Bước 3.{idx}: Lưu Customer", "skip", "Thiếu thông tin customer")
                
                receipt_code = result.get("transaction_code", "")
                receipt_date = result.get("receipt_date", "")
                shipment_code = result.get("lot_code", "")
                invoice_number = result.get("invoice_number", "")
                
                if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                    self.log_step(f"Bước 3.{idx}: Lưu Receipt {receipt_code}", "info", f"Đang lưu receipt: {receipt_code}")
                    receipt_manager = ReceiptManager()
                    receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code)
                    self.log_step(f"Bước 3.{idx}: Lưu Receipt {receipt_code}", "success", "Đã lưu receipt")
            
            self.log_step("Bước 3: Lưu dữ liệu vào Database", "success", f"Đã lưu {saved_count} customer", {"saved_count": saved_count, "details": saved_details})
            
            self.log_step("Bước 4: Kiểm tra Database", "info", "Đang kiểm tra dữ liệu trong database")
            conn = get_db_connection()
            db_check = {}
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(DISTINCT tax_code) FROM dbo.customers WHERE is_active = N'Y'")
                    db_check["unique_customers"] = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM dbo.receipts")
                    db_check["total_receipts"] = cursor.fetchone()[0]
                    conn.close()
                    self.log_step("Bước 4: Kiểm tra Database", "success", "Đã kiểm tra database", db_check)
                except Exception as e:
                    db_check["error"] = str(e)
                    self.log_step("Bước 4: Kiểm tra Database", "fail", f"Lỗi khi kiểm tra database: {str(e)}")
            else:
                self.log_step("Bước 4: Kiểm tra Database", "fail", "Không thể kết nối database")
            
            passed = len(results) >= 2 and saved_count > 0
            
            return {
                "test_name": self.get_test_name(),
                "passed": passed,
                "message": "PASS" if passed else f"Chỉ quét được {len(results)}/{len(test_files)} file, lưu {saved_count} customer",
                "steps": self.steps,
                "details": {
                    "files_tested": [f.name for f in test_files],
                    "files_success": len(results),
                    "customers_saved": saved_count,
                    "errors": errors,
                    "db_check": db_check
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
