from features.ocr.services.lines import LineService
from features.ocr.extractors.services import ServiceExtractor
from features.ocr.services.container_key import ContainerKeyService

class LineManager:
    
    def __init__(self):
        self.line_service = LineService()
        self.service_extractor = ServiceExtractor()
        self.container_key_service = ContainerKeyService()
    
    def process_and_save_lines(self, items: list, receipt_code: str, receipt_date: str, use_test_tables: bool = False) -> int:
        if not items or not receipt_code or not receipt_date:
            print(f"[LineManager] Skipping: missing information")
            return 0
        
        receipt_key = self.line_service.get_receipt_key_by_code(receipt_code, use_test_tables)
        if not receipt_key:
            print(f"[LineManager] Could not find receipt_key for receipt_code: {receipt_code}")
            return 0
        
        print(f"[LineManager] Processing {len(items)} items for receipt_code: {receipt_code}")
        saved_count = 0
        
        for item in items:
            container_number = item.get("container_number", "")
            option = item.get("option", "")
            quantity = item.get("quantity", 0)
            discount = item.get("discount", 0)
            amount = item.get("amount", 0)
            unit_price = item.get("unit_price", 0)
            tax_rate = item.get("tax")
            
            if not container_number or not option:
                print(f"[LineManager] Skipping item: missing container_number or option")
                continue
            
            if tax_rate:
                try:
                    tax_rate = int(tax_rate)
                except:
                    tax_rate = None
            else:
                tax_rate = None
            
            service_info = self.service_extractor.extract_service_info(option, unit_price, receipt_date, tax_rate)
            if not service_info:
                print(f"[LineManager] Could not extract service_info from option: '{option}'")
                continue
            
            container_key = self.container_key_service.get_container_key(
                container_size=service_info["container_size"],
                container_status=service_info["container_status"],
                container_type=service_info["container_type"],
                use_test_tables=use_test_tables
            )
            
            if not container_key:
                size = service_info["container_size"]
                status = service_info["container_status"]
                ctype = service_info["container_type"]
                print(f"[LineManager] Could not find container_key for ({size}, {status}, {ctype})")
                continue
            
            service_key = self.line_service.get_service_key(
                service_name=service_info["service_name"],
                container_key=container_key,
                from_date=service_info["from_date"],
                to_date=service_info["to_date"],
                use_test_tables=use_test_tables
            )
            
            if not service_key:
                print(f"[LineManager] Could not find service_key for service: {service_info['service_name']}")
                continue
            
            try:
                quantity_int = int(quantity) if quantity else 0
            except:
                quantity_int = 0
            
            try:
                discount_int = int(discount) if discount else 0
            except:
                discount_int = 0
            
            try:
                amount_int = int(amount) if amount else 0
            except:
                amount_int = 0
            
            success = self.line_service.save_line(
                receipt_key=receipt_key,
                container_number=container_number,
                service_key=service_key,
                quantity=quantity_int,
                discount=discount_int,
                amount=amount_int,
                use_test_tables=use_test_tables
            )
            
            if success:
                saved_count += 1
                print(f'[LineManager] Saved line successfully: container_number={container_number}')
            else:
                print(f"[LineManager] Failed to save line: container_number={container_number}")
        
        print(f"[LineManager] Saved {saved_count}/{len(items)} lines")
        return saved_count

