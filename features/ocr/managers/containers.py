from features.ocr.extractors.containers import ContainerExtractor
from features.ocr.services.containers import ContainerService
class ContainerManager:
    def __init__(self):
        self.container_extractor = ContainerExtractor()
        self.container_service = ContainerService()
    def process_and_save_containers(self, items: list) -> int:
        if not items:
            return 0
        saved_count = 0
        for item in items:
            option = item.get("option", "")
            if not option:
                continue
            container_info = self.container_extractor.extract_container_info(option)
            if not container_info:
                continue
            success = self.container_service.save_container_scd2(
                container_size=container_info["container_size"],
                container_status=container_info["container_status"],
                container_type=container_info["container_type"]
            )
            if success:
                saved_count += 1
        return saved_count
