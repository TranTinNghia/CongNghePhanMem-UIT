import traceback
from pathlib import Path
from typing import Dict
from test.test_case.base_test import BaseTest
from utils.ocr_processor import OCRProcessor
from features.ocr.managers.customers import CustomerManager
from features.ocr.managers.containers import ContainerManager
from features.ocr.managers.services import ServiceManager
from features.ocr.managers.receipts import ReceiptManager
from features.ocr.managers.lines import LineManager
from utils.db_helper import get_db_connection

class TestCase2SingleFile(BaseTest):
    def __init__(self, test_data_dir: Path):
        super().__init__()
        self.test_data_dir = test_data_dir
    
    def get_test_name(self) -> str:
        return "Test Case 2: Quét 1 file PDF"
    
    def get_test_description(self) -> str:
        return "Kiểm tra hệ thống quét 01 file PDF đúng, đủ số dòng, chính xác thông tin trên UI và ghi đúng dữ liệu vào Database"
    
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
            self.log_step("Bước 1: Tìm file PDF", "success", f"Tìm thấy file: {test_file.name}", {"file": test_file.name, "total_files": len(pdf_files)})
            
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
                    "steps": self.steps
                }
            
            self.log_step("Bước 2: Quét OCR", "success", "OCR thành công")
            
            data = result.get("data", {})
            self.log_step("Bước 3: Kiểm tra dữ liệu trích xuất", "info", "Đang kiểm tra các trường bắt buộc")
            
            required_fields = ["lot_code", "transaction_code", "receipt_date", "invoice_number", "tax_code", "customer_name", "customer_address"]
            missing_fields = [field for field in required_fields if not data.get(field) or data.get(field) == "-"]
            
            fields_status = {}
            for field in required_fields:
                value = data.get(field, "")
                fields_status[field] = {
                    "exists": bool(value and value != "-"),
                    "value": value[:50] if value else "-"
                }
            
            self.log_step("Bước 3: Kiểm tra dữ liệu trích xuất", "info", f"Kiểm tra {len(required_fields)} trường", fields_status)
            
            if missing_fields:
                self.log_step("Bước 3: Kiểm tra dữ liệu trích xuất", "fail", f"Thiếu các trường: {', '.join(missing_fields)}")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": f"Thiếu các trường: {', '.join(missing_fields)}",
                    "steps": self.steps,
                    "details": {"file": test_file.name, "data": data}
                }
            
            self.log_step("Bước 3: Kiểm tra dữ liệu trích xuất", "success", "Tất cả các trường đều có dữ liệu")
            
            items = data.get("items", [])
            if not items or len(items) == 0:
                self.log_step("Bước 4: Kiểm tra items", "fail", "Không có dữ liệu items (container details)")
                return {
                    "test_name": self.get_test_name(),
                    "passed": False,
                    "message": "Không có dữ liệu items (container details)",
                    "steps": self.steps,
                    "details": {"file": test_file.name}
                }
            
            self.log_step("Bước 4: Kiểm tra items", "success", f"Tìm thấy {len(items)} items", {"items_count": len(items)})
            
            self.log_step("Bước 5: Lưu Customer", "info", "Đang lưu thông tin customer vào database")
            tax_code = data.get("tax_code", "")
            customer_name = data.get("customer_name", "")
            customer_address = data.get("customer_address", "")
            
            customer_saved = False
            if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                customer_manager = CustomerManager()
                customer_saved = customer_manager.process_and_save_customer(tax_code, customer_name, customer_address)
                if customer_saved:
                    self.log_step("Bước 5: Lưu Customer", "success", f"Đã lưu customer: {customer_name} (MST: {tax_code})")
                else:
                    self.log_step("Bước 5: Lưu Customer", "fail", "Không thể lưu customer")
            else:
                self.log_step("Bước 5: Lưu Customer", "skip", "Thiếu thông tin customer")
            
            self.log_step("Bước 6: Lưu Receipt", "info", "Đang lưu thông tin receipt vào database")
            receipt_code = data.get("transaction_code", "")
            receipt_date = data.get("receipt_date", "")
            shipment_code = data.get("lot_code", "")
            invoice_number = data.get("invoice_number", "")
            
            receipt_saved = False
            if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                receipt_manager = ReceiptManager()
                receipt_saved = receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code)
                if receipt_saved:
                    self.log_step("Bước 6: Lưu Receipt", "success", f"Đã lưu receipt: {receipt_code}")
                else:
                    self.log_step("Bước 6: Lưu Receipt", "fail", "Không thể lưu receipt")
            else:
                self.log_step("Bước 6: Lưu Receipt", "skip", "Thiếu thông tin receipt")
            
            self.log_step("Bước 7: Lưu Containers và Services", "info", "Đang lưu containers và services")
            containers_saved = 0
            if items:
                container_manager = ContainerManager()
                containers_saved = container_manager.process_and_save_containers(items)
                self.log_step("Bước 7: Lưu Containers và Services", "info", f"Đã lưu {containers_saved} containers")
                
                if receipt_date and receipt_date != "-":
                    service_manager = ServiceManager()
                    service_manager.process_and_save_services(items, receipt_date)
                    self.log_step("Bước 7: Lưu Containers và Services", "info", "Đã lưu services")
                    
                    if receipt_code and receipt_code != "-":
                        line_manager = LineManager()
                        line_manager.process_and_save_lines(items, receipt_code, receipt_date)
                        self.log_step("Bước 7: Lưu Containers và Services", "info", "Đã lưu lines")
            
            if containers_saved > 0:
                self.log_step("Bước 7: Lưu Containers và Services", "success", f"Đã lưu {containers_saved} containers")
            else:
                self.log_step("Bước 7: Lưu Containers và Services", "fail", "Không lưu được container nào")
            
            self.log_step("Bước 8: Kiểm tra Database", "info", "Đang kiểm tra dữ liệu trong database")
            conn = get_db_connection()
            db_check = {}
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM dbo.customers WHERE tax_code = ? AND is_active = N'Y'", (tax_code,))
                    db_check["customers"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM dbo.receipts WHERE receipt_code = ?", (receipt_code,))
                    db_check["receipts"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM dbo.containers WHERE is_active = N'Y'")
                    db_check["containers"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM dbo.lines WHERE receipt_code = ?", (receipt_code,))
                    db_check["lines"] = cursor.fetchone()[0]
                    
                    conn.close()
                    self.log_step("Bước 8: Kiểm tra Database", "success", "Đã kiểm tra database", db_check)
                except Exception as e:
                    db_check["error"] = str(e)
                    self.log_step("Bước 8: Kiểm tra Database", "fail", f"Lỗi khi kiểm tra database: {str(e)}")
            else:
                self.log_step("Bước 8: Kiểm tra Database", "fail", "Không thể kết nối database")
            
            all_saved = customer_saved and receipt_saved and containers_saved > 0
            db_valid = db_check.get("customers", 0) > 0 and db_check.get("receipts", 0) > 0
            
            passed = all_saved and db_valid
            
            return {
                "test_name": self.get_test_name(),
                "passed": passed,
                "message": "PASS" if passed else f"Lưu DB thất bại: customer={customer_saved}, receipt={receipt_saved}, containers={containers_saved}, db_check={db_check}",
                "steps": self.steps,
                "details": {
                    "file": test_file.name,
                    "ocr_success": True,
                    "fields_extracted": len([f for f in required_fields if data.get(f) and data.get(f) != "-"]),
                    "items_count": len(items),
                    "customer_saved": customer_saved,
                    "receipt_saved": receipt_saved,
                    "containers_saved": containers_saved,
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
