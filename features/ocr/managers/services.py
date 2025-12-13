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
            return 0
        saved_count = 0
        for item in items:
            option = item.get("option", "")
            unit_price = item.get("unit_price", 0)
            tax_rate = item.get("tax")
            if tax_rate:
                try:
                    tax_rate = int(tax_rate)
                except:
                    tax_rate = None
            else:
                tax_rate = None
            if not option:
                continue
            service_info = self.service_extractor.extract_service_info(option, unit_price, receipt_date, tax_rate)
            if not service_info:
                continue
            container_key = self.container_key_service.get_container_key(
                container_size=service_info["container_size"],
                container_status=service_info["container_status"],
                container_type=service_info["container_type"]
            )
            if not container_key:
                size = service_info["container_size"]
                status = service_info["container_status"]
                ctype = service_info["container_type"]
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
        return saved_count
