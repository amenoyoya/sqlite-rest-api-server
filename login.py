'''
ログインAPIサーバー
'''
from flask import Flask, request, jsonify, session
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os, json
from pprint import pprint

# Flaskアプリケーション
app = Flask(__name__)

# cookieを暗号化する秘密鍵
app.config['SECRET_KEY'] = os.urandom(24)

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
@app.route('/login', methods=['POST'])
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
@app.route('/logout')
def logout():
    # セッションからusernameを取り出す
    session.pop('username', None)
    return jres(200, {
        'message': 'succeeded to logout'
    })

# ルートパスアクセスは要認証
@app.route('/', methods=['GET'])
@require_login
def index():
    pprint(request.environ)
    # Databaseサーバーの tables API を叩く
    req = Request('http://localhost:5000/tables')
    try:
        with urlopen(req) as res:
        return jres(200, json.load(res))
    except HTTPError as err:
        return jres(err.code, err.reson)
    except URLError as err:
        return jres(err.code, err.reson)

# Flaskサーバー実行
if __name__ == "__main__":
    # ログインAPIサーバーは localhost:4000 で実行
    app.run(debug=True, port=4000)
