try:
    import pymssql
    USE_PYMSSQL = True
except ImportError:
    import pyodbc
    USE_PYMSSQL = False
import yaml
import os
from typing import Optional


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
                print(f"Lỗi kết nối với pymssql: {e}")
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
        
        return conn
    except Exception as e:
        print(f"Lỗi kết nối database: {e}")
        import traceback
        traceback.print_exc()
        return None

