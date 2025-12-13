import re
from typing import Optional, Dict
class ContainerExtractor:
    def extract_container_info(self, option: str) -> Optional[Dict]:
        if not option:
            return None
        option_lower = option.lower()
        container_size = None
        container_status = None
        container_type = "GP"
        patterns = [
            r"\b(20|40|45)\s+lạnh\s+(hàng|rỗng)",
            r"\b(20|40|45)\s+(hàng|rỗng)",
            r"(hàng|rỗng)\s+(20|40|45)",
            r"\b(20|40|45)\b.*?(hàng|rỗng)",
        ]
        for pattern in patterns:
            match = re.search(pattern, option_lower)
            if match:
                if len(match.groups()) == 2:
                    if match.group(1) in ["20", "40", "45"]:
                        container_size = match.group(1)
                        container_status = match.group(2)
                    else:
                        container_status = match.group(1)
                        container_size = match.group(2)
                break
        if not container_size or not container_status:
            return None
        if "lạnh" in option_lower:
            container_type = "HC"
        status_map = {
            "hàng": "F",
            "rỗng": "E"
        }
        container_status_code = status_map.get(container_status.lower(), container_status)
        result = {
            "container_size": container_size,
            "container_status": container_status_code,
            "container_type": container_type
        }
        return result
