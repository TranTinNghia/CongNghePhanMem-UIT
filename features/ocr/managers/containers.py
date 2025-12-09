from features.ocr.extractors.containers import ContainerExtractor
from features.ocr.services.containers import ContainerService

class ContainerManager:
    
    def __init__(self):
        self.container_extractor = ContainerExtractor()
        self.container_service = ContainerService()
    
    def process_and_save_containers(self, items: list, use_test_tables: bool = False) -> int:
        if not items:
            print(f"[ContainerManager] Skipping: no items")
            return 0
        
        print(f"[ContainerManager] Processing {len(items)} items")
        saved_count = 0
        
        for item in items:
            option = item.get("option", "")
            if not option:
                print(f"[ContainerManager] Skipping item: no option")
                continue
            
            print(f"[ContainerManager] Processing item: option='{option}'")
            container_info = self.container_extractor.extract_container_info(option)
            if not container_info:
                print(f"[ContainerManager] Could not extract container_info from option: '{option}'")
                continue
            
            success = self.container_service.save_container_scd2(
                container_size=container_info["container_size"],
                container_status=container_info["container_status"],
                container_type=container_info["container_type"],
                use_test_tables=use_test_tables
            )
            
            if success:
                saved_count += 1
                print(f"[ContainerManager] Saved container successfully: {container_info}")
            else:
                print(f'[ContainerManager] Failed to save container: {container_info}')
        
        print(f"[ContainerManager] Saved {saved_count}/{len(items)} containers")
        return saved_count

