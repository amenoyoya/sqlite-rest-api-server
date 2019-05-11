from flask import g, Flask, request
from sqlalchemy.sql import insert
from api.tables import define_tables_api
from api.functions import get_db, jres
from pprint import pprint

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['database'] = 'database.sqlite3'

# Tables API 定義
define_tables_api(app, '/tables')

@app.route('/tables/<string:table>/rows', methods=['POST'])
def insert_rows(table):
  ''' tableにデータinsert '''
  db = get_db(app)
  # テーブルの存在確認
  if table not in db.meta.tables:
    return jres(400, {
      'message': f'table "{table}" not exists'
    })
  # データ挿入
  with db.connect() as con:
    result = con.execute(insert(
      db.meta.tables[table], values=request.json['values']
    ))
    return jres(201, {
      'message': f'{result.rowcount} rows inserted into table "{table}"'
    })

# Flaskサーバー実行
if __name__ == "__main__":
  app.run(debug=True)
