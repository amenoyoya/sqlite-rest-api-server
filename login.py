# encoding: utf-8
'''
ログインAPIサーバー

1. database/rest.py: Databaseサーバー(localhost:5000)を起動
2. this file: ログインAPサーバー(localhost:4000)を起動
3. curlコマンドでログイン
    ```
    $ curl -c cookie -d 'username=admin' -d 'password=adminadmin' http://localhost:4000/login

    # リダイレクト有効なら 4. の手順は不要
    $ curl -L -c cookie -d 'username=admin' -d 'password=adminadmin' http://localhost:4000/login
    ```
4. ログイン後にDatabaseサーバーからtables情報取得
    ```
    $ curl -b cookie http://localhost:4000
    # => http://localhost:4000 => GET http://localhost:5000/tables
    ```
'''
from database.libs.frasco import Frasco, Response
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os, json
# from pprint import pprint

# 認証ユーザークラス
class AuthUser:
    # 認証可能なユーザー
    users = {
        'user1': {
            'username': 'admin', 'password': 'adminadmin'
        },
        'user2': {
            'username': 'hoge', 'password': 'fugafuga'
        }
    }

    def __init__(self, id):
        self.id = id
        self.username = AuthUser.users[id]['username']
        self.password = AuthUser.users[id]['password']

    # 認証処理
    @staticmethod
    def auth(data):
        username = data.get('username')
        password = data.get('password')
        # 登録済みのユーザーか判定
        for id, user in AuthUser.users.items():
            if username == user['username'] and password == user['password']:
                return AuthUser(id)

    # セッション保存処理
    @staticmethod
    def save(user):
        return user.id
    
    # セッション復元処理
    @staticmethod
    def load(session_id):
        return AuthUser(session_id)


# Flaskアプリケーション
## 認証処理用のユーザークラスをAuthUserとする
app = Frasco(__name__, User=AuthUser)

# 認証処理API
@app.auth('/login', '/logout', Response.text('ログアウトしました\n'))
def login(user):
    if user:
        # succeeded to login => redirect to /
        return Response.redirect('/')
    # failed to login
    return Response.text('認証エラー: ユーザー名かパスワードが違います\n', 400)

# ルートパスアクセスは要認証
@app.get('/')
@app.secret(Response.text('先にログインしてください: /login\n'))
def index():
    data = {'message': app.current_user.username + ' としてログイン中'}
    # pprint(request.environ)
    # Databaseサーバーの tables API を叩く
    req = Request('http://localhost:5000/tables')
    try:
        with urlopen(req) as res:
            data.update(json.load(res))
            return Response.json(data)
    except HTTPError as err:
        data.update({'error': err.reason})
        return Response.json(data, err.code)
    except URLError as err:
        data.update({'error': err.reason})
        return Response.json(data, err.code)

# Flaskサーバー実行
if __name__ == "__main__":
    # ログインAPIサーバーは localhost:4000 で実行
    app.run(debug=True, port=4000)
