from typing import Optional
from datetime import datetime
from utils.db_helper import get_db_connection

class ReceiptService:
    
    def _convert_date_format(self, date_str: str) -> Optional[str]:
        if not date_str or date_str == "-":
            return None
        
        date_formats = [
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y",
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue
        
        return None
    
    def _get_customer_key_by_tax_code(self, tax_code: str, cursor) -> Optional[str]:
        if not tax_code or tax_code == "-":
            return None
        
        tax_code = tax_code.strip()
        cursor.execute(
            "SELECT customer_key FROM dbo.customers WHERE tax_code = ? AND is_active = N'Y'",
            (tax_code,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def save_receipt_scd1(self, receipt_code: str, receipt_date: str, shipment_code: str, invoice_number: str, tax_code: str) -> bool:
        if not receipt_code or not receipt_date or not shipment_code or not invoice_number or not tax_code:
            return False
        
        receipt_code = receipt_code.strip()[:10]
        shipment_code = shipment_code.strip()[:10]
        invoice_number = invoice_number.strip()[:10]
        tax_code = tax_code.strip()
        
        converted_date = self._convert_date_format(receipt_date)
        if not converted_date:
            print(f"[ReceiptService] Could not convert date format: {receipt_date}")
            return False
        
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            customer_key = self._get_customer_key_by_tax_code(tax_code, cursor)
            if not customer_key:
                print(f"[ReceiptService] Could not find customer_key for tax_code: {tax_code}")
                conn.rollback()
                conn.close()
                return False
            
            cursor.execute(
                "SELECT receipt_key, receipt_code, receipt_date, shipment_code, invoice_number, customer_key FROM dbo.receipts WHERE receipt_code = ?",
                (receipt_code,)
            )
            existing_receipt = cursor.fetchone()
            
            if existing_receipt:
                old_receipt_key = existing_receipt[0]
                old_receipt_code = existing_receipt[1] or ""
                old_receipt_date = str(existing_receipt[2] or "")
                old_shipment_code = existing_receipt[3] or ""
                old_invoice_number = existing_receipt[4] or ""
                old_customer_key = existing_receipt[5] or ""
                
                receipt_code_clean = receipt_code.strip()
                receipt_date_clean = converted_date.strip()
                shipment_code_clean = shipment_code.strip()
                invoice_number_clean = invoice_number.strip()
                customer_key_clean = customer_key.strip()
                
                old_receipt_code_clean = (old_receipt_code or "").strip()
                old_receipt_date_clean = old_receipt_date.strip()
                old_shipment_code_clean = (old_shipment_code or "").strip()
                old_invoice_number_clean = (old_invoice_number or "").strip()
                old_customer_key_clean = (old_customer_key or "").strip()
                
                has_changes = (
                    receipt_code_clean != old_receipt_code_clean or
                    receipt_date_clean != old_receipt_date_clean or
                    shipment_code_clean != old_shipment_code_clean or
                    invoice_number_clean != old_invoice_number_clean or
                    customer_key_clean != old_customer_key_clean
                )
                
                if not has_changes:
                    conn.commit()
                    conn.close()
                    print(f"[ReceiptService] Receipt with receipt_code {receipt_code} has no changes, skipping update.")
                    return True
                
                cursor.execute(
                    """UPDATE dbo.receipts 
                       SET receipt_code = ?, receipt_date = ?, shipment_code = ?, invoice_number = ?, customer_key = ?
                       WHERE receipt_key = ?""",
                    (receipt_code, converted_date, shipment_code, invoice_number, customer_key, old_receipt_key)
                )
            else:
                cursor.execute(
                    """INSERT INTO dbo.receipts (receipt_code, receipt_date, shipment_code, invoice_number, customer_key)
                       VALUES (?, ?, ?, ?, ?)""",
                    (receipt_code, converted_date, shipment_code, invoice_number, customer_key)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ReceiptService] Error saving receipt: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

