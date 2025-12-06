import os
from typing import Optional

class DocumentCountService:
    
    def get_document_count(self, upload_folder: str = "uploads") -> Optional[int]:
        try:
            if not os.path.exists(upload_folder):
                return 0
            
            files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]
            
            return len(files)
        except Exception as e:
            print(f"[DocumentCountService] Error counting documents: {e}")
            return None

