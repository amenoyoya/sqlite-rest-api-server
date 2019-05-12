'''
# WSGI
WSGI (Web Server Gateway Interface, ウィズギー)
: Pythonにおいて、WebサーバとWebアプリケーション（もしくはWebアプリケーションフレームワーク）を接続するための標準化されたインタフェース定義

WSGIにはサーバ側とアプリケーション側が存在する
WSGIは、リクエスト情報・レスポンスヘッダ・レスポンス本文を、両者の間でどのようにやりとりするかをPythonのAPIとして定義している

Webサーバにリクエストが来ると、次のような流れでやりとりが行なわれる:
1. サーバ側が、クライアントからリクエストを受ける
2. サーバ側は、アプリケーション側がエントリポイントとして提供するcallableオブジェクト（関数やクラスインスタンスなど `__call__` が定義されたオブジェクト）を呼び出す
  - 引数として環境変数と1つのコールバック用callableオブジェクトを渡す
3. アプリケーション側は、このコールバック用callableオブジェクトを呼び出すことでステータスコードとレスポンスヘッダをサーバ側に伝え、さらに本文を生成するiterableオブジェクト（イテレータやリストなど）を戻り値として返す
4. サーバ側は、これらを用いてクライアントへのレスポンスを生成する

## WSGIアプリケーションの例
```python
def application(environ, start_response):
  start_response('200 OK', [('Content-Type', 'text/plain')])
  yield b'Hello World\n'
```

解説:
1. WSGIアプリケーションは、callableオブジェクト (`__call__`が定義されたオブジェクト) として定義する（この例では `application` 関数）
  - 引数 `environ` としてCGIと同様の環境変数が渡される
  - 引数 `start_response` として、ステータスコードとレスポンスヘッダを受け取るcallableオブジェクトが渡される
2. `start_response` を呼び出して、ステータスコードとレスポンスヘッダを設定する
3. WSGIアプリケーションの戻り値は、本文を生成するiteratableオブジェクトである必要がある
  - この例ではPythonのジェネレータ機能を使って実現している
'''

# Python's bundled WSGI server
from wsgiref.simple_server import make_server

# The application interface is a callable object
def application(environ, start_response):
  # Build the response body possibly
  # # using the supplied environ dictionary
  response_body = 'Request method: %s' % environ['REQUEST_METHOD']
  
  # HTTP response code and message
  status = '200 OK'

  # HTTP headers expected by the client
  # They must be wrapped as a list of tupled pairs:
  # [(Header name, Header value)].
  response_headers = [
    ('Content-Type', 'text/plain'),
    ('Content-Length', str(len(response_body)))
  ]
  
  # Send them to the server using the supplied function
  start_response(status, response_headers)
  
  # Return the response body. Notice it is wrapped
  # in a list although it could be any iterable.
  return [response_body.encode('utf-8')]

def get_environments (environ, start_response):
  # Sorting and stringifying the environment key, value pairs
  response_body = [
    '%s: %s' % (key, value) for key, value in sorted(environ.items())
  ]
  response_body = '\n'.join(response_body)

  status = '200 OK'
  response_headers = [
    ('Content-Type', 'text/plain'),
    ('Content-Length', str(len(response_body)))
  ]
  start_response(status, response_headers)
  return [response_body.encode('utf-8')]

if __name__ == "__main__":
  # Instantiate the server
  httpd = make_server (
    'localhost', # The host name
    8051, # A port number where to wait for the request
    #application # The application object name, in this case a function
    get_environments
  )
  
  # Wait for a single request, serve it and quit
  #httpd.handle_request()

  print("Serving on port 8051...")
  # Serve until process is killed
  httpd.serve_forever()
