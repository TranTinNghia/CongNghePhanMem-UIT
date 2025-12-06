try:
    import pymssql
    USE_PYMSSQL = True
except ImportError:
    import pyodbc
    USE_PYMSSQL = False
import yaml
import os
from typing import Optional


class CursorWrapper:
    """Wrapper cho cursor để chuyển đổi ? thành %s cho pymssql"""
    def __init__(self, cursor, is_pymssql):
        self._cursor = cursor
        self._is_pymssql = is_pymssql
    
    def __getattr__(self, name):
        return getattr(self._cursor, name)
    
    def execute(self, query, params=None):
        if self._is_pymssql and params is not None:
            # Chuyển đổi ? thành %s cho pymssql
            query = query.replace('?', '%s')
        if params:
            return self._cursor.execute(query, params)
        else:
            return self._cursor.execute(query)
    
    def executemany(self, query, params_list):
        if self._is_pymssql:
            # Chuyển đổi ? thành %s cho pymssql
            query = query.replace('?', '%s')
        return self._cursor.executemany(query, params_list)


class ConnectionWrapper:
    """Wrapper để xử lý sự khác biệt giữa pymssql và pyodbc"""
    def __init__(self, conn):
        self._conn = conn
        self._is_pymssql = USE_PYMSSQL
    
    def __getattr__(self, name):
        # Nếu là autocommit và dùng pymssql, return False (pymssql mặc định không autocommit)
        if name == 'autocommit' and self._is_pymssql:
            return False
        return getattr(self._conn, name)
    
    def __setattr__(self, name, value):
        # Nếu set autocommit và dùng pymssql, bỏ qua (pymssql không hỗ trợ set autocommit)
        if name == 'autocommit' and self._is_pymssql:
            # pymssql mặc định không autocommit, không cần set
            return
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(self._conn, name, value)
    
    def cursor(self):
        """Trả về wrapped cursor để tự động chuyển đổi ? thành %s"""
        cursor = self._conn.cursor()
        return CursorWrapper(cursor, self._is_pymssql)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if hasattr(self._conn, 'close'):
            self._conn.close()


def load_config():
    # Ưu tiên đọc từ environment variables (cho production/deploy)
    db_url = os.environ.get('DB_URL')
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME', 'btn')
    
    if db_url and db_username and db_password:
        # Tạo config từ environment variables
        return {
            "url": db_url,
            "username": db_username,
            "password": db_password,
            "database": db_name
        }
    
    # Fallback: đọc từ file config.yaml (cho local development)
    try:
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config["users"]
    except FileNotFoundError:
        print("Lỗi đọc config: File config/config.yaml không tồn tại và không có environment variables")
        print("Vui lòng tạo file config/config.yaml hoặc set các environment variables: DB_URL, DB_USERNAME, DB_PASSWORD")
        return None
    except Exception as e:
        print(f"Lỗi đọc config: {e}")
        return None


def get_db_connection():
    config = load_config()
    if not config:
        return None
    
    try:
        # Xử lý cả environment variables và file config
        if "database" in config:
            # Từ environment variables
            url = config["url"]
            username = config["username"]
            password = config["password"]
            database = config["database"]
        else:
            # Từ file config.yaml
            url = config["url"]
            username = config["username"]
            password = config["password"]
            
            # Parse database từ URL
            if "databaseName=" in url:
                database = url.split("databaseName=")[1].split(";")[0]
            else:
                database = "btn"
        
        # Parse server và port từ URL
        if "//" in url:
            server_part = url.split("//")[1]
            if ":" in server_part:
                server = server_part.split(":")[0]
                port_part = server_part.split(":")[1]
                port = int(port_part.split(";")[0] if ";" in port_part else port_part)
            else:
                server = server_part.split(";")[0] if ";" in server_part else server_part
                port = 1433
        else:
            server = "localhost"
            port = 1433
        
        # Sử dụng pymssql nếu có (không cần ODBC drivers)
        if USE_PYMSSQL:
            try:
                conn = pymssql.connect(
                    server=server,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    timeout=10
                )
            except Exception as e:
                error_msg = str(e)
                print(f"Lỗi kết nối với pymssql: {e}")
                # Kiểm tra nếu là lỗi kết nối qua tunnel
                if "Unexpected EOF" in error_msg or "connection failed" in error_msg.lower():
                    print("\n⚠️  CẢNH BÁO: Cloudflare Quick Tunnel có thể không hỗ trợ TCP cho SQL Server.")
                    print("   Vui lòng xem file CLOUDFLARE_TCP_FIX.md để biết các giải pháp thay thế.")
                raise Exception(f"Không thể kết nối database với pymssql: {e}")
        else:
            # Fallback: sử dụng pyodbc (cần ODBC drivers)
            drivers = [
                "ODBC Driver 18 for SQL Server",
                "ODBC Driver 17 for SQL Server",
                "ODBC Driver 13 for SQL Server",
                "SQL Server"
            ]
            
            conn = None
            for driver in drivers:
                try:
                    conn_str = (
                        f"DRIVER={{{driver}}};"
                        f"SERVER={server},{port};"
                        f"DATABASE={database};"
                        f"UID={username};"
                        f"PWD={password};"
                        f"TrustServerCertificate=yes;"
                    )
                    conn = pyodbc.connect(conn_str)
                    break
                except Exception as e:
                    print(f"Thử driver {driver} thất bại: {e}")
                    continue
            
            if not conn:
                raise Exception("Không thể kết nối với bất kỳ ODBC driver nào")
        
        # Wrap connection để xử lý sự khác biệt giữa pymssql và pyodbc
        return ConnectionWrapper(conn)
    except Exception as e:
        print(f"Lỗi kết nối database: {e}")
        import traceback
        traceback.print_exc()
        return None

