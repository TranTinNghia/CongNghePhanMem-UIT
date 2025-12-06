import re
from typing import Optional, Dict


class ContainerExtractor:
    
    def extract_container_info(self, option: str) -> Optional[Dict]:
        if not option:
            print(f"[ContainerExtractor] Skipping: empty option")
            return None
        
        print(f"[ContainerExtractor] Processing option: '{option}'")
        option_lower = option.lower()
        
        container_size = None
        container_status = None
        container_type = "GP"
        
        patterns = [
            r'\b(20|40|45)\s+lạnh\s+(hàng|rỗng)',
            r'\b(20|40|45)\s+(hàng|rỗng)',
            r'(hàng|rỗng)\s+(20|40|45)',
            r'\b(20|40|45)\b.*?(hàng|rỗng)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, option_lower)
            if match:
                print(f"[ContainerExtractor] Pattern match: {pattern}, groups: {match.groups()}")
                if len(match.groups()) == 2:
                    if match.group(1) in ['20', '40', '45']:
                        container_size = match.group(1)
                        container_status = match.group(2)
                    else:
                        container_status = match.group(1)
                        container_size = match.group(2)
                break
        
        if not container_size or not container_status:
            print(f"[ContainerExtractor] Missing information: container_size={container_size}, container_status={container_status}")
            return None
        
        if 'lạnh' in option_lower:
            container_type = "HC"
            print(f"[ContainerExtractor] Container type: HC (refrigerated)")
        else:
            print(f"[ContainerExtractor] Container type: GP (general)")
        
        status_map = {
            "hàng": "F",
            "rỗng": "E"
        }
        container_status_code = status_map.get(container_status.lower(), container_status)
        print(f"[ContainerExtractor] Container status: {container_status} -> {container_status_code}")
        
        result = {
            "container_size": container_size,
            "container_status": container_status_code,
            "container_type": container_type
        }
        
        print(f"[ContainerExtractor] Extract successful: {result}")
        return result

