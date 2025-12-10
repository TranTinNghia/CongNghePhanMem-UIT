from features.ocr.services.receipts import ReceiptService

class ReceiptManager:
    
    def __init__(self):
        self.receipt_service = ReceiptService()
    
    def process_and_save_receipt(self, receipt_code: str, receipt_date: str, shipment_code: str, invoice_number: str, tax_code: str) -> bool:
        if not receipt_code or not receipt_date or not shipment_code or not invoice_number or not tax_code:
            print(f"[ReceiptManager] Skipping: missing information (receipt_code={receipt_code}, receipt_date={receipt_date}, shipment_code={shipment_code}, invoice_number={invoice_number}, tax_code={tax_code})")
            return False
        
        if receipt_code == "-" or receipt_date == "-" or shipment_code == "-" or invoice_number == "-" or tax_code == "-":
            print(f"[ReceiptManager] Skipping: one or more fields are '-'")
            return False
        
        print(f'[ReceiptManager] Processing receipt: receipt_code={receipt_code}, shipment_code={shipment_code}, invoice_number={invoice_number}')
        
        success = self.receipt_service.save_receipt_scd1(
            receipt_code=receipt_code,
            receipt_date=receipt_date,
            shipment_code=shipment_code,
            invoice_number=invoice_number,
            tax_code=tax_code
        )
        
        if success:
            print(f"[ReceiptManager] Saved receipt successfully: {receipt_code}")
        else:
            print(f"[ReceiptManager] Failed to save receipt: {receipt_code}")
        
        return success

