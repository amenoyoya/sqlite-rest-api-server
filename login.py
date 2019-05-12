'''
ログインAPIサーバー
'''
from flask import Flask, request, jsonify
from urllib.request import Request, urlopen
import json
from pprint import pprint

# Flaskアプリケーション
app = Flask(__name__)

def jres(status_code, content):
  ''' ステータスコード付きでJsonレスポンス作成 '''
  res = jsonify(content)
  res.status_code = status_code
  return res

@app.route('/', methods=['GET'])
def index():
  pprint(request.environment)
  req = Request('http://localhost:5000/tables')
  try:
    with urlopen(req) as res:
      return jres(200, json.load(res))
  except urllib.error.HTTPError as err:
    return jres(err.code, err.reson)
  except urllib.error.URLError as err:
    return jres(err.code, err.reson)

# Flaskサーバー実行
if __name__ == "__main__":
  # ログインAPIサーバーは localhost:4000 で実行
  app.run(debug=True, port=4000)
