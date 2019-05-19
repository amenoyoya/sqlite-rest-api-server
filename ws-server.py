from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi

# 接続しているクライアントのリスト
ws_list = set()

# Websocket通信のハンドラ(WSGI規格に準拠)
def chat_handle(environ, start_response):
	ws = environ['wsgi.websocket']
	ws_list.add(ws) # 新規接続してきたクライアントをリストに追加

	print('enter:', len(ws_list), environ['REMOTE_ADDR'], environ['REMOTE_PORT'])

    # 通信ループ
	while True:
		msg = ws.receive() # メッセージ受信
		if msg is None:
			break # メッセージが受信できなければ通信終了
		remove = set()
		for s in ws_list:
			try:
				s.send(msg) # 受信したメッセージをオウム返しする
			except Exception:
				remove.add(s) # メッセージ送信できなかったクライアントを除外リストに追加
		for s in remove:
			ws_list.remove(s) # メッセージ送信できなかったクライアントを削除

	print('exit:', environ['REMOTE_ADDR'], environ['REMOTE_PORT'])
	ws_list.remove(ws) # 新規接続してきたクライアントとの通信終了

# WSGIルーティング
def myapp(environ, start_response):
	path = environ['PATH_INFO']
	if path == '/':
		start_response('200 OK', [('Content-Type', 'text/html')])
		return [open('index.html', 'rb').read()]
	elif path == '/chat':
		return chat_handle(environ, start_response)
	else:
		start_response('404 Not Found.', [('Content-Type', 'text/plain')])
		return ['not found'.encode('utf-8')]

if __name__ == '__main__':
	server = pywsgi.WSGIServer(('localhost', 8080), myapp, handler_class=WebSocketHandler)
	server.serve_forever()
