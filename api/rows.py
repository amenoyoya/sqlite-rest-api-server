'''
API for rows
'''

from sqlalchemy.sql import insert, select, update, delete, and_, or_, tuple_, asc, desc
from flask import request
from .RPN import RPN
from .functions import Database, jres, get_db

def define_rows_api(app, route):
  ''' row操作API定義
  params:
    app flask.Flask: flaskアプリケーション
    route str: REST API url
  '''
  def build_select(table, selects):
    ''' selectターゲットのクエリを作成 '''
    if selects is None: return [table]
    return [table if select == '*' else table.columns[select] for select in selects]

  def build_where(table, where_rpn):
    ''' selectのwhere句のクエリを作成 '''
    # 演算子定義
    op = {
      '<': lambda x, y: x < y, '<=': lambda x, y: x <= y,
      '>': lambda x, y: x > y, '>=': lambda x, y: x >= y,
      '=': lambda x, y: x == y, '!=': lambda x, y: x != y,
      'and': lambda x, y: and_(x, y), 'or': lambda x, y: or_(x, y),
      'like': lambda x, y: x.like(y), 'in': lambda x, y: tuple_(x).in_([(e,) for e in y]),
    }
    # 変数定義
    op.update(table.columns)
    # 逆ポーランド記法でクエリ生成
    return RPN(where_rpn, op)[0]

  def build_order_by(query, table, orders):
    ''' selectのorder_by句のクエリを作成 '''
    for order in orders:
      if order[0] == 'asc':
        query = query.order_by(asc(table.columns[order[1]]))
      elif order[0] == 'desc':
        query = query.order_by(desc(table.columns[order[1]]))
    return query

  def build_query(query, table):
    ''' requests.jsonの内容からクエリを生成 '''
    json = request.json
    # where
    if json and 'where' in json:
      query = query.where(build_where(table, json['where']))
    # order_by
    if json and 'order_by' in json:
      query = build_order_by(query, table, json['order_by'])
    # limit
    if json and 'limit' in json:
      query = query.limit(json['limit'])
    return query
  
  # --- rows REST API --- #

  @app.route(f'{route}/<string:name>/rows', methods=['GET'])
  def get_rows(name):
    ''' tableにデータinsert '''
    db = get_db(app)
    # テーブルの存在確認
    if name not in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" not exists'
      })
    # データ取得
    with db.connect() as con:
      tbl = db.meta.tables[name]
      json = request.json
      query = select(build_select(tbl, None if json is None else json.get('select')))
      result = con.execute(build_query(query, tbl))
      return jres(200, {
        'values': [{key: val for key, val in row.items()} for row in result]
      })

  @app.route(f'{route}/<string:name>/rows', methods=['POST'])
  def insert_rows(name):
    ''' tableにデータinsert '''
    db = get_db(app)
    # テーブルの存在確認
    if name not in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" not exists'
      })
    # データ挿入
    with db.connect() as con:
      result = con.execute(insert(
        db.meta.tables[name], values=request.json['values']
      ))
      return jres(201, {
        'message': f'{result.rowcount} rows inserted into table "{name}"'
      })

  @app.route(f'{route}/<string:name>/rows', methods=['PUT'])
  def update_rows(name):
    ''' tableのデータをupdate '''
    db = get_db(app)
    # テーブルの存在確認
    if name not in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" not exists'
      })
    # データ更新
    with db.connect() as con:
      tbl = db.meta.tables[name]
      query = update(tbl)
      result = con.execute(build_query(query, tbl), **request.json['values'])
      return jres(200, {
        'message': f'{result.rowcount} rows updated in table "{name}"'
      })

  @app.route(f'{route}/<string:name>/rows', methods=['DELETE'])
  def delete_rows(name):
    ''' tableのデータをdelete '''
    db = get_db(app)
    # テーブルの存在確認
    if name not in db.meta.tables:
      return jres(400, {
        'message': f'table "{name}" not exists'
      })
    # データ削除
    with db.connect() as con:
      tbl = db.meta.tables[name]
      query = delete(tbl)
      result = con.execute(build_query(query, tbl))
      return jres(200, {
        'message': f'{result.rowcount} rows deleted from table "{name}"'
      })
