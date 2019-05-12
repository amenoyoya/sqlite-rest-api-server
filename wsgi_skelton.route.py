from wsgiref.simple_server import make_server
import json

def application(env, start_response):
  path = env['PATH_INFO']
  if path == '/':
    start_response('200 OK', [('Content-type', 'text/plain')])
    return [b'Hello World']
  elif path == '/foo':
    start_response('200 OK', [('Content-type', 'text/plain')])
    return [b'foo']
  elif path == '/json':
    start_response('200 OK', [('Content-type', 'application/json')])
    return [
      json.dumps({
        'status': 200,
        'message': 'Jsonテスト'
      }).encode('utf-8')
    ]
  else:
    start_response('404 Not Found', [('Content-type', 'text/plain')])
    return [b'404 Not Found']

if __name__ == "__main__":
  httpd = make_server('localhost', 8051, application)
  print("Serving on port 8051...")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('Quit server...')
