import pyodbc
import yaml
from typing import Optional


def load_config():
    try:
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config["users"]
    except Exception as e:
        print(f"Lỗi đọc config: {e}")
        return None


def get_db_connection():
    config = load_config()
    if not config:
        return None
    
    try:
        url = config["url"]
        
        if "//" in url:
            server_part = url.split("//")[1]
            if ":" in server_part:
                server = server_part.split(":")[0]
                port_part = server_part.split(":")[1]
                port = port_part.split(";")[0] if ";" in port_part else port_part
            else:
                server = server_part.split(";")[0] if ";" in server_part else server_part
                port = "1433"
        else:
            server = "localhost"
            port = "1433"
        
        if "databaseName=" in url:
            database = url.split("databaseName=")[1].split(";")[0]
        else:
            database = "btn"
        
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
                    f"UID={config['username']};"
                    f"PWD={config['password']};"
                    f"TrustServerCertificate=yes;"
                )
                conn = pyodbc.connect(conn_str)
                break
            except:
                continue
        
        if not conn:
            raise Exception("Không thể kết nối với bất kỳ ODBC driver nào")
        
        return conn
    except Exception as e:
        print(f"Lỗi kết nối database: {e}")
        return None

