from http.server import HTTPServer, SimpleHTTPRequestHandler
import cgi
import os
import sys

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
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"ファイル '{file_name}' がアップロードされました。".encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"エラー: ファイルが見つかりません。")
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8002):
    server_address = ('', port)
    httpd = HTTPServer(server_address, UploadHandler)
    print(f"サーバーを開始: http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == '__main__':
    # コマンドライン引数からポート番号を取得（デフォルトは8002）
    port = 8002
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    run_server(port)
