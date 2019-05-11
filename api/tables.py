'''
API for tables
'''

from sqlalchemy import Table, Column
from flask import request
from .functions import Database, jres, get_db

def define_tables_api(app, route):
  ''' table操作API定義
  params:
    app flask.Flask: flaskアプリケーション
    route str: REST API url
  '''
  def get_table_scheme(table):
    ''' tableスキーマ取得 '''
    return [{
      'name': c.name,
      'type': c.type.python_type.__name__,
      'nullable': c.nullable,
      'primary_key': c.primary_key
    } for c in table.columns]

  @app.route(route, methods=['GET'])
  def get_tables():
    ''' table列挙 '''
    db = get_db(app)
    return jres(200, {
      'tables': {
        tbl: get_table_scheme(db.meta.tables[tbl]) for tbl in db.meta.tables
      }
    })

  @app.route(f'{route}/<string:name>', methods=['GET'])
  def get_table(name):
    ''' tableスキーマ取得 '''
    db = get_db(app)
    # テーブルの存在確認
    if name not in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" not exists'
      })
    return jres(200, {
      'table': get_table_scheme(db.meta.tables[name])
    })

  @app.route(f'{route}/<string:name>', methods=['POST'])
  def create_table(name):
    ''' table作成 '''
    db = get_db(app)
    # テーブルの存在確認
    if name in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" already exists'
      })
    # 新規テーブル作成
    columns = [
      Column(column[0], Database.types[column[1]], **column[2] if len(column) > 2 else {}) for column in request.json['columns']
    ]
    Table(name, db.meta, *columns).create()
    return jres(201, {
      'message': f'table "{name}" created"'
    })

  @app.route(route, methods=['DELETE'])
  def drop_tables():
    ''' table全削除 '''
    db = get_db(app)
    db.meta.drop_all()
    return jres(200, {
      'message': f'all tables deleted"'
    })

  @app.route(f'{route}/<string:name>', methods=['DELETE'])
  def drop_table(name):
    ''' table削除 '''
    db = get_db(app)
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
