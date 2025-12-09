import traceback
from pathlib import Path
from typing import Dict
from test.test_case.base_test import BaseTest
from utils.ocr_processor import OCRProcessor

class TestCase3UIUpdate(BaseTest):
    def __init__(self, test_data_dir: Path):
        super().__init__()
        self.test_data_dir = test_data_dir
    
    def get_test_name(self) -> str:
        return "Test Case 3: UI cập nhật đúng thông tin"
    
    def get_test_description(self) -> str:
        return "Kiểm tra UI có cập nhật đúng các thông tin sau khi quét OCR"
    
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
            self.log_step("Bước 3: Kiểm tra các trường hiển thị trên UI", "info", "Đang kiểm tra các trường bắt buộc")
            
            required_fields = ["lot_code", "transaction_code", "receipt_date", "invoice_number", "tax_code", "customer_name", "customer_address"]
            
            fields_check = {}
            for field in required_fields:
                value = data.get(field, "")
                exists = bool(value and value != "-")
                fields_check[field] = {
                    "exists": exists,
                    "value": value[:50] if value else "-",
                    "status": "ok" if exists else "missing"
                }
                if exists:
                    self.log_step(f"Bước 3: Kiểm tra trường {field}", "success", f"Trường {field} có giá trị: {value[:50]}")
                else:
                    self.log_step(f"Bước 3: Kiểm tra trường {field}", "fail", f"Trường {field} không có giá trị hoặc là '-'")
            
            all_fields_present = all(fields_check[f]["exists"] for f in required_fields)
            
            if all_fields_present:
                self.log_step("Bước 3: Kiểm tra các trường hiển thị trên UI", "success", "Tất cả các trường đều có dữ liệu")
            else:
                missing = [f for f in required_fields if not fields_check[f]["exists"]]
                self.log_step("Bước 3: Kiểm tra các trường hiển thị trên UI", "fail", f"Thiếu các trường: {', '.join(missing)}")
            
            self.log_step("Bước 4: Kiểm tra items (Container details)", "info", "Đang kiểm tra items")
            items = data.get("items", [])
            items_check = {
                "exists": bool(items and len(items) > 0),
                "count": len(items) if items else 0
            }
            
            if items_check["exists"]:
                self.log_step("Bước 4: Kiểm tra items (Container details)", "success", f"Tìm thấy {items_check['count']} items")
                
                for idx, item in enumerate(items[:5], 1):
                    item_fields = ["container_number", "option", "quantity", "unit_price", "tax", "discount", "amount"]
                    item_check = {}
                    for field in item_fields:
                        value = item.get(field, "")
                        item_check[field] = {
                            "exists": bool(value and value != "-" and value != ""),
                            "value": str(value)[:30] if value else "-"
                        }
                    self.log_step(f"Bước 4.{idx}: Kiểm tra item {idx}", "info", f"Item {idx} có {len([f for f in item_fields if item_check[f]['exists']])}/{len(item_fields)} trường", item_check)
            else:
                self.log_step("Bước 4: Kiểm tra items (Container details)", "fail", "Không có items")
            
            passed = all_fields_present and items_check["exists"]
            
            return {
                "test_name": self.get_test_name(),
                "passed": passed,
                "message": "PASS" if passed else "Thiếu một số trường hoặc không có items",
                "steps": self.steps,
                "details": {
                    "file": test_file.name,
                    "fields_check": fields_check,
                    "items_check": items_check,
                    "all_fields_present": all_fields_present
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
