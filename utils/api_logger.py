from datetime import datetime
from flask import request, session
import json
from utils.auth_helper import verify_token

class ApiLogger:
    @staticmethod
    def log_request():
        if request.path.startswith('/api/') or request.path.startswith('/ocr/'):
            print("\n" + "="*80)
            print(f"[API REQUEST] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)

            print(f"📍 URL: {request.method} {request.path}")
            if request.query_string:
                print(f"📍 Query String: {request.query_string.decode('utf-8')}")

            print("\n📋 HEADERS:")
            headers_dict = dict(request.headers)
            for key, value in headers_dict.items():
                if key.lower() == 'authorization':
                    if value.startswith('Bearer '):
                        token = value[7:]
                        if len(token) > 20:
                            masked_token = token[:10] + "..." + token[-10:]
                        else:
                            masked_token = token[:10] + "..."
                        print(f"   {key}: Bearer {masked_token}")
                        print(f"   🔑 JWT Token (full): {token}")
                    else:
                        print(f"   {key}: {value}")
                elif key.lower() in ['cookie', 'set-cookie']:
                    print(f"   {key}: [REDACTED]")
                else:
                    print(f"   {key}: {value}")

            print("\n📦 REQUEST BODY/PAYLOAD:")
            try:
                if request.is_json:
                    payload = request.get_json(silent=True)
                    if payload:
                        print(f"   {json.dumps(payload, indent=2, ensure_ascii=False)}")
                    else:
                        print("   (Empty JSON)")
                elif request.form:
                    form_data = dict(request.form)
                    if 'password' in form_data:
                        form_data['password'] = '[REDACTED]'
                    print(f"   Form Data: {json.dumps(form_data, indent=2, ensure_ascii=False)}")
                elif request.files:
                    files_info = {}
                    for key, file in request.files.items():
                        current_pos = file.tell() if hasattr(file, 'tell') else 0
                        try:
                            file.seek(0, 2)
                            size = file.tell()
                            file.seek(current_pos)
                        except:
                            size = 'unknown'

                        files_info[key] = {
                            'filename': file.filename,
                            'content_type': file.content_type,
                            'size': size
                        }
                    print(f"   Files: {json.dumps(files_info, indent=2, ensure_ascii=False)}")
                else:
                    try:
                        raw_data = request.get_data(as_text=True, cache=True)
                        if raw_data:
                            print(f"   Raw Data: {raw_data[:500]}")
                        else:
                            print("   (No body)")
                    except:
                        print("   (Cannot read body)")
            except Exception as e:
                print(f"   Error reading body: {e}")

            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                try:
                    payload = verify_token(token)
                    if payload:
                        print(f"\n🔐 JWT TOKEN PAYLOAD:")
                        print(f"   {json.dumps(payload, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"\n🔐 JWT TOKEN: (Invalid or expired)")
                except Exception as e:
                    print(f"\n🔐 JWT TOKEN: (Error decoding: {e})")

            if session:
                session_info = {
                    'user_id': session.get('user_id'),
                    'username': session.get('username'),
                    'role': session.get('role'),
                    'has_jwt_token': 'jwt_token' in session
                }
                print(f"\n👤 SESSION INFO:")
                print(f"   {json.dumps(session_info, indent=2, ensure_ascii=False)}")

            print("-"*80)

    @staticmethod
    def log_response(response):
        if request.path.startswith('/api/') or request.path.startswith('/ocr/'):
            print("\n📤 RESPONSE:")

            print(f"   Status Code: {response.status_code}")

            print(f"   Response Headers:")
            for key, value in response.headers:
                if key.lower() not in ['set-cookie']:
                    print(f"      {key}: {value}")

            try:
                if hasattr(response, 'get_data'):
                    original_data = response.get_data()
                    response.set_data(original_data)

                    if original_data:
                        try:
                            response_data = original_data.decode('utf-8') if isinstance(original_data, bytes) else original_data
                            json_data = json.loads(response_data)
                            print(f"   Response Body (JSON):")
                            print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                        except:
                            response_data = original_data.decode('utf-8') if isinstance(original_data, bytes) else str(original_data)
                            if len(response_data) > 500:
                                print(f"   Response Body (Raw, truncated): {response_data[:500]}...")
                            else:
                                print(f"   Response Body (Raw): {response_data}")
                    else:
                        print("   Response Body: (Empty)")
            except Exception as e:
                print(f"   Error reading response: {e}")

            print("="*80 + "\n")

        return response

