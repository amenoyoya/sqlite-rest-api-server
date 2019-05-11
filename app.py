import os
from flask import Flask, g, request, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import Integer, String, Text, Float
from pprint import pprint

# Database basic types
DatabaseTypes = {
  'int': Integer, 'str': String, 'text': Text,  'num': Float 
}

class Database:
  ''' SQLAlchemyデータベース '''
  def __init__(self, db_name):
    self.engine = create_engine('sqlite:///' + db_name)
    self.meta = MetaData(self.engine, reflect=True)

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['database'] = 'database.sqlite3'

def jres(status_code, content):
  # ステータスコード付きでJsonレスポンス作成
  res = jsonify(content)
  res.status_code = status_code
  return res

def get_db():
  ''' Databaseのconnectionを取得 '''
  if not hasattr(g, 'databse'):
    g.database = Database(app.config['database'])
  return g.database

def get_table_scheme(table):
  ''' tableスキーマ取得 '''
  return [{
    'name': c.name,
    'type': c.type.python_type.__name__,
    'nullable': c.nullable,
    'primary_key': c.primary_key
  } for c in table.columns]

@app.route('/tables', methods=['GET'])
def get_tables():
  ''' table列挙 '''
  db = get_db()
  return jres(200, {
    'tables': {
      tbl: get_table_scheme(db.meta.tables[tbl]) for tbl in db.meta.tables
    }
  })

@app.route('/tables/<string:name>', methods=['GET'])
def get_table(name):
  ''' tableスキーマ取得 '''
  db = get_db()
  # テーブルの存在確認
  if name not in db.meta.tables:
    return jres(400, {
      'message': f'table "{name}" not exists'
    })
  return jres(200, {
    'table': get_table_scheme(db.meta.tables[name])
  })

@app.route('/tables/<string:name>', methods=['POST'])
def create_table(name):
  ''' table作成 '''
  db = get_db()
  # テーブルの存在確認
  if name in db.meta.tables:
    return jres(400, {
      'message': f'table "{name}" already exists'
    })
  # 新規テーブル作成
  columns = [
    Column(column[0], DatabaseTypes[column[1]], **column[2] if len(column) > 2 else {}) for column in request.json['columns']
  ]
  Table(name, db.meta, *columns).create()
  return jres(201, {
    'message': f'table "{name}" created"'
  })

@app.route('/tables', methods=['DELETE'])
def drop_tables():
  ''' table全削除 '''
  db = get_db()
  db.meta.drop_all()
  return jres(200, {
    'message': f'all tables deleted"'
  })

@app.route('/tables/<string:name>', methods=['DELETE'])
def drop_table(name):
  ''' table削除 '''
  db = get_db()
  # テーブルの存在確認
  if name not in db.meta.tables:
    return jres(400, {
      'message': f'table "{name}" not exists'
    })
  # テーブル削除
  db.meta.tables[name].drop()
  return jres(200, {
    'message': f'table "{name}" deleted"'
  })

# Flaskサーバー実行
if __name__ == "__main__":
  app.run(debug=True)
