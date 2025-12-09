import os
import sys
    
wsgi_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, wsgi_dir)

root_dir = os.path.dirname(wsgi_dir)
sys.path.insert(0, root_dir)

from app import app
application = app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
