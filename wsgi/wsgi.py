import os
import sys

wsgi_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, wsgi_dir)

root_dir = os.path.dirname(wsgi_dir)
sys.path.insert(0, root_dir)

from app import app

wsgi_application = app

try:
    from asgiref.wsgi import WsgiToAsgi
    
    class ImprovedASGIWrapper:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app
            self._asgi_app = WsgiToAsgi(wsgi_app)
        
        async def __call__(self, scope, receive, send):
            try:
                await self._asgi_app(scope, receive, send)
            except Exception as e:
                error_msg = str(e)
                if "UnexpectedMessageError" in type(e).__name__ or "ASGIHTTPState" in error_msg:
                    if scope.get("type") == "http":
                        try:
                            await send({
                                "type": "http.response.start",
                                "status": 500,
                                "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
                            })
                            await send({
                                "type": "http.response.body",
                                "body": b"Internal Server Error",
                                "more_body": False,
                            })
                        except Exception:
                            pass
                    return
                raise
    
    asgi_application = ImprovedASGIWrapper(app)
    
    application = asgi_application
    
except ImportError:
    application = app
    asgi_application = app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
