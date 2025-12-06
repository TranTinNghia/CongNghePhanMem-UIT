import re
import traceback
from typing import Dict, List, Optional
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from utils.text_formatter import TextFormatter

class OCRProcessor:
    
    def __init__(self):
        self.text_formatter = TextFormatter()
    
    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> str:
        if not use_ocr:
            try:
                all_text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            all_text += text + "\n"
                
                if len(all_text.strip()) > 50:
                    return all_text
                else:
                    print("PDF không có text layer hoặc text quá ít, chuyển sang OCR...")
            except Exception as e:
                print(f"Lỗi khi đọc text trực tiếp từ PDF: {e}, chuyển sang OCR...")
        
        try:
            images = convert_from_path(pdf_path, dpi=300)
            all_text = ""
            for image in images:
                try:
                    text = pytesseract.image_to_string(image, lang='vie+eng')
                except:
                    text = pytesseract.image_to_string(image, lang='eng')
                all_text += text + "\n"
            return all_text
        except Exception as e:
            print(f"Lỗi khi đọc PDF bằng OCR: {e}")
            return ""
    
    def extract_lot_code(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Mã\s*lô\s*hàng|Lô\s*hàng)[:\s]+([A-Z0-9]{6,})',
            r'Lô[:\s]+([A-Z0-9]{6,})',
            r'\b([0-9]{8,})\b',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                code = match.group(1).strip()
                if len(code) <= 15 and code.isalnum():
                    return code
        return None
    
    def extract_transaction_code(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Mã\s*giao\s*dịch|Giao\s*dịch)[:\s]+([A-Z0-9]+)',
            r'([A-Z0-9]{10,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                if len(code) >= 8:
                    return code
        return None
    
    def extract_receipt_date(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Ngày\s*biên\s*nhận|Ngày)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?:\s+\d{1,2}:\d{2})?)',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Số\s*hóa\s*đơn|Hóa\s*đơn)[:\s]+([A-Z0-9]{6,})',
            r'(?:Invoice|HD)[:\s]+([A-Z0-9]{6,})',
            r'Số\s*hóa\s*đơn[:\s]+([0-9]{6,})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                invoice_num = match.group(1).strip()
                if len(invoice_num) >= 6:
                    if invoice_num.isdigit():
                        if int(invoice_num) > 1000:
                            return invoice_num
                    else:
                        return invoice_num
        return None
    
    def extract_tax_code(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Mã\s*số\s*thuế|MST|Tax\s*code|Mã\s*thuế)[:\s]*([0-9\-]{9,15})',
            r'(?:Mã\s*số\s*thuế|MST)[:\s]*([0-9]{3}[-]?[0-9]{3}[-]?[0-9]{3}[-]?[0-9]{0,4})',
            r'(?:Mã\s*số\s*thuế|MST)[:\s]*([0-9]{9,13})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                code = match.group(1).strip().replace('-', '').replace('.', '').replace(' ', '')
                if 9 <= len(code) <= 13 and code.isdigit():
                    return code
        
        mst_keywords = re.finditer(r'(?:Mã\s*số\s*thuế|MST|Mã\s*thuế)', text, re.IGNORECASE)
        for keyword_match in mst_keywords:
            start_pos = keyword_match.end()
            end_pos = min(start_pos + 50, len(text))
            context = text[start_pos:end_pos]
            
            number_match = re.search(r'([0-9]{2,3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{0,4})', context)
            if number_match:
                code = number_match.group(1).strip().replace('-', '').replace('.', '').replace(' ', '')
                if 9 <= len(code) <= 13 and code.isdigit():
                    return code
        
        return None
    
    def extract_customer_name(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Tên\s*khách\s*hàng|Khách\s*hàng|Customer\s*name)[:\s]+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s\.,]+?)(?:\n|Mã|Số|Địa|Ngày|$)',
            r'(CÔNG\s*TY[\s\wÀ-ỹ,\.]+?)(?:\n|Mã|Số|Địa|Ngày|$)',
            r'(CTY[\s\wÀ-ỹ,\.]+?)(?:\n|Mã|Số|Địa|Ngày|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip() if match.groups() else match.group(0).strip()
                name = re.sub(r'[^\w\sÀ-ỹ,\.]', '', name)
                name = re.sub(r'\s+', ' ', name).strip()
                name = re.sub(r'^(?:Tên\s*khách\s*hàng|Khách\s*hàng|Customer)[:\s]+', '', name, flags=re.IGNORECASE)
                
                name = re.sub(r'\bCông\s+T\b', 'Công Ty', name, flags=re.IGNORECASE)
                
                if len(name) > 5:
                    return self.text_formatter.format_text(name, is_company_name=True)
        return None
    
    def extract_customer_address(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:Địa\s*chỉ|Address)[:\s]+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ0-9\s\.,\-\–\—/]+?)(?:\n{2,}|Mã\s*giao\s*dịch|Mã\s*lô|Số\s*hóa\s*đơn|Ngày\s*biên|Chi\s*tiết|$)',
            r'(?:Địa\s*chỉ|Address)[:\s]+([^\n]+?)(?:\n\s*\n|(?:\n|^)\s*(?:Mã\s*giao\s*dịch|Mã\s*lô|Số\s*hóa|Ngày|Chi\s*tiết))',
            r'Địa\s*chỉ[:\s]+([A-ZÀ-ỸĐ][^\n]*(?:[A-ZÀ-ỸĐ0-9][^\n]*)*?)(?:\n\s*(?:Mã|Số|Ngày|Chi)|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                address = match.group(1).strip()
                address = re.sub(r'^(?:Địa\s*chỉ|Address)[:\s]+', '', address, flags=re.IGNORECASE)
                address = re.sub(r'\s+', ' ', address)
                address = re.sub(r'\s*(?:Mã\s*giao\s*dịch|Mã\s*lô|Số\s*hóa|Ngày|Chi\s*tiết).*$', '', address, flags=re.IGNORECASE)
                address = address.strip()
                
                if len(address) > 10 and re.search(r'[A-ZÀ-ỸĐa-zà-ỹđ]', address):
                    return self.text_formatter.format_text(address, is_company_name=False)
        
        address_match = re.search(r'Địa\s*chỉ[:\s]+(.+?)(?=\n\s*(?:Mã|Số|Ngày|Chi|$))', text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if address_match:
            address = address_match.group(1).strip()
            address = re.sub(r'\s+', ' ', address)
            if len(address) > 10 and re.search(r'[A-ZÀ-ỸĐa-zà-ỹđ]', address):
                return self.text_formatter.format_text(address, is_company_name=False)
        
        return None
    
    def parse_service_row(self, line: str, container_number: str) -> Optional[Dict]:
        line = line.strip()
        if not line:
            return None
        
        line_clean = re.sub(r'[A-Z]{4}[0-9]{7,}', '', line).strip()
        line_clean = re.sub(r'\*{5,}', '', line_clean).strip()
        
        is_phu_thu_7_9_ngay = bool(re.search(r'7\s*[-–—>→]\s*9\s*ngày', line_clean, re.IGNORECASE))
        
        parts = line_clean.split()
        
        if len(parts) < 5:
            return None
        data_start_idx = -1
        pattern_type = None
        
        skip_indices = set()
        if is_phu_thu_7_9_ngay:
            for i in range(len(parts)):
                part = parts[i]
                if part == '7' or part == '9':
                    context = ' '.join(parts[max(0, i-2):min(len(parts), i+3)])
                    if re.search(r'7\s*[-–—>→]\s*9\s*ngày', context, re.IGNORECASE):
                        skip_indices.add(i)
                elif re.search(r'7\s*[-–—>→]\s*9', part, re.IGNORECASE):
                    skip_indices.add(i)
        
        for i in range(len(parts) - 4):
            try:
                if i in skip_indices:
                    continue
                    
                qty = parts[i]
                
                if not qty.isdigit() or int(qty) > 10:
                    continue
                
                if i + 4 < len(parts):
                    price = parts[i + 1].replace(',', '').replace('.', '')
                    tax = parts[i + 2]
                    discount = parts[i + 3]
                    amount = parts[i + 4].replace(',', '').replace('.', '')
                    
                    if (price.isdigit() and int(price) > 1000 and
                        tax.isdigit() and int(tax) < 100 and
                        discount.isdigit() and
                        amount.isdigit() and int(amount) > 1000):
                        
                        data_start_idx = i
                        pattern_type = 'normal'
                        break
                
                if i + 6 < len(parts):
                    num1 = parts[i + 1]
                    price_part = parts[i + 2].replace(',', '').replace('.', '')
                    tax = parts[i + 3]
                    discount = parts[i + 4]
                    num2 = parts[i + 5]
                    amount_part = parts[i + 6].replace(',', '').replace('.', '')
                    
                    if num1.isdigit() and num2.isdigit() and price_part.isdigit() and amount_part.isdigit():
                        price = num1 + price_part
                        amount = num2 + amount_part
                        
                        if (int(price) > 1000 and
                            tax.isdigit() and int(tax) < 100 and
                            discount.isdigit() and
                            int(amount) > 1000):
                            
                            data_start_idx = i
                            pattern_type = 'with_num'
                            break
            except:
                continue
        
        if data_start_idx == -1:
            return None
        if pattern_type == 'with_num':
            option_after = parts[data_start_idx + 7:] if data_start_idx + 7 < len(parts) else []
        else:
            option_after = parts[data_start_idx + 5:] if data_start_idx + 5 < len(parts) else []
        option_before = parts[:data_start_idx] if data_start_idx > 0 else []
        
        if option_before and len(option_before) > 0:
            option_text = " ".join(option_before)
        elif option_after and len(option_after) > 0:
            option_text = " ".join(option_after)
        else:
            return None
        
        if not option_before and 'hàng' in option_text and '→' in option_text:
            match = re.match(r'(hàng\s+\d+\s*→\s*\d+\s*Ngày)\s+(.+)', option_text, re.IGNORECASE)
            if match:
                hang_part = match.group(1)
                other_part = match.group(2)
                option = f"{other_part} {hang_part}"
            else:
                option = option_text
        else:
            option = option_text
        
        option = re.sub(r'\b[A-Z]{4}[0-9]{3}\b', '', option).strip()
        option = re.sub(r'\s+', ' ', option)
        
        if re.match(r'^hàng\s+\d+\s*→\s*\d+\s*Ngày$', option, re.IGNORECASE):
            nang_match = re.search(r'nâng\s+(\d+)', line, re.IGNORECASE)
            if nang_match:
                so_nang = nang_match.group(1)
                option = f"Phụ thu phí nâng {so_nang} {option}"
            else:
                option = f"Phụ thu phí nâng {option}"
        
        giao_match = re.match(r'(Giao\s+cont\s+hàng\s+\d+\s*G?P)\s*(Hàng)?', option, re.IGNORECASE)
        if giao_match:
            base = giao_match.group(1)
            base = re.sub(r'(\d+)\s*G?\s*P', r'\1GP', base)
            option = f"{base} Hàng"
        
        if is_phu_thu_7_9_ngay:
            option = re.sub(r'\s+1$', '', option).strip()
        
        if not option or len(option) < 10:
            return None
        
        if is_phu_thu_7_9_ngay:
            quantity = "1"
        else:
            quantity = parts[data_start_idx]
        
        if pattern_type == 'with_num':
            unit_price_str = parts[data_start_idx + 1] + parts[data_start_idx + 2]
            tax = parts[data_start_idx + 3]
            discount_str = parts[data_start_idx + 4]
            amount_str = parts[data_start_idx + 5] + parts[data_start_idx + 6]
        else:
            unit_price_str = parts[data_start_idx + 1]
            tax = parts[data_start_idx + 2]
            discount_str = parts[data_start_idx + 3]
            amount_str = parts[data_start_idx + 4]
        
        def clean_money(value: str) -> int:
            if not value:
                return 0
            value = value.replace(".", "").replace(",", "")
            try:
                return int(value)
            except:
                return 0
        
        unit_price = clean_money(unit_price_str)
        
        result = {
            "container_number": container_number,
            "option": option,
            "quantity": quantity,
            "unit_price": unit_price,
            "tax": tax,
            "discount": clean_money(discount_str),
            "amount": clean_money(amount_str)
        }
        
        return result
    
    def extract_container_items_from_table(self, pdf_path: str) -> List[Dict]:
        items = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.splitlines()
                    
                    i = 0
                    current_container = None
                    container_count = 0
                    
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        if not line:
                            i += 1
                            continue
                        
                        line_upper = line.upper()
                        
                        if any(keyword in line_upper for keyword in ['SỐ ĐK', 'SỐ CONTAINER', 'PHƯƠNG ÁN', 'SỐ LƯỢNG', 'ĐƠN GIÁ']):
                            i += 1
                            continue
                        
                        container_match = re.search(r'([A-Z]{4}[0-9]{7,})', line)
                        
                        if container_match:
                            current_container = container_match.group(1)
                            parsed = self.parse_service_row(line, current_container)
                            if parsed and parsed.get('option'):
                                items.append(parsed)
                        
                        i += 1
                    
                    if items:
                        break
            
            return items
            
        except Exception as e:
            print(f"Lỗi khi đọc bảng bằng pdfplumber: {e}")
            traceback.print_exc()
        
        return []
    
    def extract_container_items(self, text: str, pdf_path: str = None) -> List[Dict]:
        if pdf_path:
            items = self.extract_container_items_from_table(pdf_path)
            if items:
                valid_items = []
                for item in items:
                    option = item.get('option', '')
                    
                    if re.search(r'[A-Z]{4}[0-9]{7,}', option):
                        continue
                    
                    if option and len(option) >= 10:
                        option_upper = option.upper()
                        if any(keyword in option_upper for keyword in ['PHỤ', 'THU', 'GIAO', 'NÂNG', 'HẠ', 'HÀNG', 'CONT', 'PHÍ', 'NGÀY', 'GP']):
                            valid_items.append(item)
                
                if valid_items:
                    return valid_items
        
        return self.extract_container_items_from_text(text)
    
    def extract_container_items_from_text(self, text: str) -> List[Dict]:
        items = []
        lines = text.split('\n')
        
        container_pattern = r'([A-Z]{4}[0-9]{7,})'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in ['SỐ CONTAINER', 'PHƯƠNG ÁN', 'ĐƠN GIÁ']):
                continue
            
            container_match = re.search(container_pattern, line)
            
            if container_match:
                current_container = container_match.group(1)
                parsed = self.parse_service_row(line, current_container)
                if parsed and parsed.get('option'):
                    items.append(parsed)
        
        return items
    
    def process_ocr(self, pdf_path: str) -> Dict:
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {
                "success": False,
                "error": "Không thể đọc được nội dung từ PDF"
            }
        
        items = self.extract_container_items(text, pdf_path)
        
        result = {
            "lot_code": self.extract_lot_code(text) or "-",
            "transaction_code": self.extract_transaction_code(text) or "-",
            "receipt_date": self.extract_receipt_date(text) or "-",
            "invoice_number": self.extract_invoice_number(text) or "-",
            "tax_code": self.extract_tax_code(text) or "-",
            "customer_name": self.extract_customer_name(text) or "-",
            "customer_address": self.extract_customer_address(text) or "-",
            "items": items
        }
        
        return {
            "success": True,
            "data": result
        }
