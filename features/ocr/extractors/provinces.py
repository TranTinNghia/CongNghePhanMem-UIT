import re
from typing import Optional

class ProvinceExtractor:
    
    def extract_province_name(self, address: str) -> Optional[str]:
        if not address:
            print(f"[ProvinceExtractor] Skipping: empty address")
            return None
        
        print(f"[ProvinceExtractor] Processing address: '{address}'")
        
        patterns = [
            r"Tỉnh\s+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s\–\-]+?)(?:,|$)",
            r"Thành\s+Phố\s+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s\–\-]+?)(?:,|$)",
            r"Tỉnh\s+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s\–\-]+)",
            r"Thành\s+Phố\s+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s\–\-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address, re.IGNORECASE | re.MULTILINE)
            if match:
                province_name = match.group(1).strip()
                if province_name:
                    print(f"[ProvinceExtractor] Found province: '{province_name}'")
                    return province_name
        
        print(f"[ProvinceExtractor] Could not find province in address: '{address}'")
        return None

