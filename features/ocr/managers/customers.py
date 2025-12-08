from features.ocr.extractors.provinces import ProvinceExtractor
from features.ocr.services.provinces import ProvinceService
from features.ocr.services.customers import CustomerService

class CustomerManager:
    
    def __init__(self):
        self.province_extractor = ProvinceExtractor()
        self.province_service = ProvinceService()
        self.customer_service = CustomerService()
    
    def process_and_save_customer(self, tax_code: str, customer_name: str, address: str) -> bool:
        if not tax_code or not customer_name or not address:
            print(f"[CustomerManager] Skipping: missing information (tax_code={tax_code}, customer_name={customer_name}, address={address})")
            return False
        
        print(f'[CustomerManager] Processing customer: tax_code={tax_code}, customer_name={customer_name}')
        print(f"[CustomerManager] Address: '{address}'")
        
        province_name = self.province_extractor.extract_province_name(address)
        province_key = None
        
        if province_name:
            print(f"[CustomerManager] Finding province_key for: '{province_name}'")
            province_key = self.province_service.get_province_key(province_name)
            if province_key:
                print(f"[CustomerManager] Found province_key: {province_key}")
            else:
                print(f"[CustomerManager] Could not find province_key for: '{province_name}'")
        else:
            print(f"[CustomerManager] Could not extract province_name from address")
        
        success = self.customer_service.save_customer_scd2(
            tax_code=tax_code,
            customer_name=customer_name,
            address=address,
            province_key=province_key
        )
        
        if success:
            print(f'[CustomerManager] Saved customer successfully: {tax_code}')
        else:
            print(f"[CustomerManager] Failed to save customer: {tax_code}")
        
        return success

