from features.ocr.extractors.services import ServiceExtractor
from features.ocr.services.container_key import ContainerKeyService
from features.ocr.services.services import ServiceService

class ServiceManager:
    
    def __init__(self):
        self.service_extractor = ServiceExtractor()
        self.container_key_service = ContainerKeyService()
        self.service_service = ServiceService()
    
    def process_and_save_services(self, items: list, receipt_date: str) -> int:
        if not items or not receipt_date:
            print(f"[ServiceManager] Skipping: no items or receipt_date")
            return 0
        
        print(f"[ServiceManager] Processing {len(items)} items with receipt_date: {receipt_date}")
        saved_count = 0
        
        for item in items:
            option = item.get("option", "")
            unit_price = item.get("unit_price", 0)
            tax_rate = item.get("tax")
            
            print(f"[ServiceManager] Processing item: option='{option}', unit_price={unit_price}, tax_rate={tax_rate}")
            
            if tax_rate:
                try:
                    tax_rate = int(tax_rate)
                except:
                    tax_rate = None
            else:
                tax_rate = None
            
            if not option:
                print(f"[ServiceManager] Skipping item: no option")
                continue
            
            service_info = self.service_extractor.extract_service_info(option, unit_price, receipt_date, tax_rate)
            if not service_info:
                print(f"[ServiceManager] Could not extract service_info from option: '{option}'")
                continue
            
            container_key = self.container_key_service.get_container_key(
                container_size=service_info["container_size"],
                container_status=service_info["container_status"],
                container_type=service_info["container_type"]
            )
            
            if not container_key:
                print(f"[ServiceManager] Could not find container_key for ({service_info['container_size']}, {service_info['container_status']}, {service_info['container_type']})")
                continue
            
            success = self.service_service.save_service_scd2(
                service_name=service_info["service_name"],
                container_key=container_key,
                from_date=service_info["from_date"],
                to_date=service_info["to_date"],
                unit_price=service_info["unit_price"],
                tax_rate=service_info["tax_rate"]
            )
            
            if success:
                saved_count += 1
                print(f"[ServiceManager] Saved service successfully: {service_info['service_name']}")
            else:
                print(f"[ServiceManager] Failed to save service: {service_info['service_name']}")
        
        print(f"[ServiceManager] Saved {saved_count}/{len(items)} services")
        return saved_count

