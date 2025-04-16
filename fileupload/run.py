from http.server import HTTPServer, SimpleHTTPRequestHandler
import cgi
import os
import sys
import socket

class UploadHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # upload.htmlをトップページとして返す
        if self.path == '/':
            self.path = '/upload.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/upload':
            # Content-Typeヘッダーを確認
            content_type = self.headers['Content-Type']
            
            # フォームデータを解析
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type}
            )
            
            # ファイルフィールドの確認
            if 'file' in form:
                file_item = form['file']
                
                # ファイル名を取得
                file_name = os.path.basename(file_item.filename)
                
                # ファイルを保存
                with open(file_name, 'wb') as f:
                    f.write(file_item.file.read())
                
                # 結果を返す
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                message = f"ファイル '{file_name}' がアップロードされました。"
                self.wfile.write(message.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                message = "エラー: ファイルが見つかりません。"
                self.wfile.write(message.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def get_ip_address():
    """ローカルIPアドレスを取得する関数"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 外部に接続しようとすることでローカルIPを取得（実際には接続しない）
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # 接続できない場合はループバックアドレスを返す
    finally:
        s.close()
    return ip

def run_server(port=8002):
    server_address = ('', port)
    httpd = HTTPServer(server_address, UploadHandler)
    ip = get_ip_address()
    print(f"サーバーを開始: http://{ip}:{port}/")
    print(f"ローカルアクセス: http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == '__main__':
    # コマンドライン引数からポート番号を取得（デフォルトは8002）
    port = 8002
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    run_server(port)
