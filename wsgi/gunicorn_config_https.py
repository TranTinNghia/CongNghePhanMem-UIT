import multiprocessing

bind = "0.0.0.0:5000"
backlog = 2048

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

import os

# Lấy thư mục root (một level lên từ wsgi/)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

keyfile = os.path.join(root_dir, "config", "certs", "key.pem")
certfile = os.path.join(root_dir, "config", "certs", "cert.pem")

accesslog = "-"
errorlog = "-"
loglevel = "warning"  # Giảm log level để bỏ qua SSL warnings không quan trọng
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# SSL configuration
ssl_version = 2  # TLS 1.2
do_handshake_on_connect = True
suppress_ragged_eofs = True
proc_name = "baitapnhom"
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

preload_app = True
max_requests = 1000
max_requests_jitter = 50

graceful_timeout = 30
