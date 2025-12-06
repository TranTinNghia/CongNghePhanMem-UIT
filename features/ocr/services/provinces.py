from typing import Optional
from utils.db_helper import get_db_connection

class ProvinceService:
    
    def get_province_key(self, province_name: str) -> Optional[str]:
        if not province_name:
            return None
        
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            province_name_clean = province_name.strip()
            print(f"[ProvinceService] Finding province_key for: '{province_name_clean}'")
            
            cursor.execute(
                "SELECT province_key FROM dbo.provinces WHERE LOWER(LTRIM(RTRIM(old_province))) = LOWER(LTRIM(RTRIM(?))) AND is_active = N'Y'",
                (province_name_clean,)
            )
            result = cursor.fetchone()
            
            if result:
                print(f"[ProvinceService] Found province_key: {result[0]}")
                conn.close()
                return result[0]
            
            province_name_no_dash = province_name_clean.replace('–', '-').replace('—', '-')
            if province_name_no_dash != province_name_clean:
                cursor.execute(
                    "SELECT province_key FROM dbo.provinces WHERE LOWER(LTRIM(RTRIM(old_province))) = LOWER(LTRIM(RTRIM(?))) AND is_active = N'Y'",
                    (province_name_no_dash,)
                )
                result = cursor.fetchone()
                if result:
                    print(f"[ProvinceService] Found province_key (after replacing dash): {result[0]}")
                    conn.close()
                    return result[0]
            
            cursor.execute(
                "SELECT province_key FROM dbo.provinces WHERE LOWER(LTRIM(RTRIM(old_province))) LIKE LOWER(LTRIM(RTRIM(?))) AND is_active = N'Y'",
                (f'%{province_name_clean}%',)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"[ProvinceService] Found province_key (LIKE): {result[0]}")
                return result[0]
            
            print(f"[ProvinceService] Could not find province_key for: '{province_name_clean}'")
            return None
        except Exception as e:
            print(f"[ProvinceService] Error querying province: {e}")
            try:
                conn.close()
            except:
                pass
            return None

