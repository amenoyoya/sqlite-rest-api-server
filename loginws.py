'''
ログインAPIサーバー（Websocket版）
=> 失敗：動作しない
'''
from database.lib.ws import WebsocketClient
from flask import Flask, request, jsonify, session
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os, json, time
from pprint import pprint

class LoginServer(WebsocketClient):
    def __init__(self, ws_host):
        super(LoginServer, self).__init__()

        self.app = Flask(__name__)
        self.app.config.from_object(__name__)
        # cookieを暗号化する秘密鍵
        self.app.config['SECRET_KEY'] = os.urandom(24)
        # WebsocketClientをサーバーモードで実行
        self.open_server(ws_host)

    def on_connect(self):
        '''
        WebsocketClient接続時に、Flaskサーバーも生成
        '''
        def jres(status_code, content):
            ''' ステータスコード付きでJsonレスポンス作成 '''
            res = jsonify(content)
            res.status_code = status_code
            return res

        # 認証処理デコレータ
        def require_login(func):
            def wrapper(*args, **kargs):
                # セッションに username が保存されていればログイン済み
                if session.get('username') is not None:
                    return func(*args, **kargs)
                # ログインされていない場合はエラーレスポンスを返す
                return jres(401, {
                    'message': 'Unauthorized'
                })
            return wrapper

        # ログイン処理
        @self.app.route('/login', methods=['POST'])
        def login():
            # 認証
            username = request.form.get('username')
            if username == 'admin':
                # セッションにユーザ名を保存
                session['username'] = request.form['username']
                return jres(200, {
                'message': 'succeeded to login'
                })
            return jres(400, {
                'message': 'invalid user'
            })

        # ログアウト処理
        @self.app.route('/logout')
        def logout():
            # セッションからusernameを取り出す
            session.pop('username', None)
            return jres(200, {
                'message': 'succeeded to logout'
            })

        # ルートパスアクセスは要認証
        @self.app.route('/', methods=['GET'])
        @require_login
        def index():
            pprint(request.environ)
            # Databaseサーバーの tables API を叩く
            self.send_message('tables://{"method": "GET"}')
            # メッセージ受信まで待つ
            while not hasattr(self, 'data'):
                time.sleep(1)
            return jres(200, self.data)
        
        # Flaskサーバー実行 localhost:4000
        self.app.run(debug=False, port=4000)
    
    def on_message_recieved(self, message):
        ''' DatabaseWebsocketServerからメッセージ受信 '''
        self.data = json.loads(message)

if __name__ == "__main__":
    # localhost:5000 (DatabaseWebsocketServer) に接続
    LoginServer('ws://localhost:5000')
