import re
from typing import Optional, Dict
from datetime import datetime
class ServiceExtractor:
    def extract_service_info(self, option: str, unit_price: int, receipt_date: str, tax_rate: Optional[int] = None) -> Optional[Dict]:
        if not option or not receipt_date:
            return None
        option_lower = option.lower()
        service_name = None
        container_size = None
        container_status = None
        container_type = "GP"
        if "phụ thu phí nâng" in option_lower:
            arrow_pattern = re.search(r"(\d+)\s*->\s*(\d+)\s*ngày", option_lower)
            lon_hon_pattern = re.search(r"lớn\s+hơn\s+(\d+)\s*ngày", option_lower)
            so_ngay_pattern = re.search(r"(\d+)\s*ngày", option_lower)
            if arrow_pattern:
                service_name = f"Phụ thu phí nâng {arrow_pattern.group(1)}->{arrow_pattern.group(2)} ngày"
            elif lon_hon_pattern:
                service_name = f"Phụ thu phí nâng lớn hơn {lon_hon_pattern.group(1)} ngày"
            elif so_ngay_pattern:
                service_name = f"Phụ thu phí nâng {so_ngay_pattern.group(1)} ngày"
            size_patterns = [
                r"\b(20|40|45)\s+(?:lạnh\s+)?(?:hàng|rỗng)",
                r"\b(20|40|45)\b",
            ]
            for pattern in size_patterns:
                match = re.search(pattern, option_lower)
                if match:
                    container_size = match.group(1)
                    break
            if "lạnh" in option_lower:
                container_type = "HC"
            if "rỗng" in option_lower:
                container_status = "E"
            elif "hàng" in option_lower:
                container_status = "F"
        elif "giao cont" in option_lower:
            if "hàng" in option_lower:
                service_name = "Giao cont hàng"
                container_status = "F"
            elif "rỗng" in option_lower:
                service_name = "Giao cont rỗng"
                container_status = "E"
            size_patterns = [
                r"\b(20|40|45)\s+lạnh",
                r"\b(20|40|45)\b",
            ]
            for pattern in size_patterns:
                match = re.search(pattern, option_lower)
                if match:
                    container_size = match.group(1)
                    break
            if "lạnh" in option_lower:
                container_type = "HC"
        if not service_name or not container_size or not container_status:
            return None
        from_date = self._get_start_of_year(receipt_date)
        to_date = self._get_end_of_year(receipt_date)
        if not from_date or not to_date:
            return None
        result = {
            "service_name": service_name,
            "container_size": container_size,
            "container_status": container_status,
            "container_type": container_type,
            "from_date": from_date,
            "to_date": to_date,
            "unit_price": unit_price,
            "tax_rate": tax_rate if tax_rate is not None else 8
        }
        return result
    def _get_start_of_year(self, receipt_date: str) -> Optional[str]:
        try:
            date_formats = [
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y",
                "%d-%m-%Y %H:%M",
                "%d-%m-%Y",
            ]
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(receipt_date.strip(), fmt)
                    break
                except:
                    continue
            if not parsed_date:
                return None
            year = parsed_date.year
            return f"{year}-01-01 00:00:00"
        except:
            return None
    def _get_end_of_year(self, receipt_date: str) -> Optional[str]:
        try:
            date_formats = [
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y",
                "%d-%m-%Y %H:%M",
                "%d-%m-%Y",
            ]
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(receipt_date.strip(), fmt)
                    break
                except:
                    continue
            if not parsed_date:
                return None
            year = parsed_date.year
            return f"{year}-12-31 23:59:59"
        except:
            return None
