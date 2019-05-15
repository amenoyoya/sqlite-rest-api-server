'''
Databaseサーバー（REST API版）
'''

from flask import g, Flask, request, jsonify
from lib.db import Database
import os, json

# 使用するデータベース
DATABASE = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['migrated'] = False # migration実行フラグ

def jres(status_code, content):
    ''' ステータスコード付きでJsonレスポンス作成 '''
    res = jsonify(content)
    res.status_code = status_code
    return res

def migrate(db, migration):
    ''' マイグレーション用JSONファイルからデータベース構築 '''
    if not os.path.exists(migration):
        return False
    with open(migration, 'rb') as f:
        data = json.load(f)
    config = data.get('config')
    tables = data.get('tables')
    values = data.get('values')
    if config and config.get('recreate'):
        # recreateフラグが立っているならテーブルを削除
        db.drop_tables()
    # table構築
    if not isinstance(tables, dict):
        return False
    for table, columns in tables.items():
        if db.is_table_exists(table):
            continue
        # 存在しないtableを構築し、データ流し込み
        if db.create_table(table, columns) == False:
            return False
        rows = values.get(table) if isinstance(values, dict) else None
        if rows and db.insert_rows(table, rows) == False:
            return False
    return True

def get_db():
    ''' Databaseのconnectionを取得 '''
    if not hasattr(g, 'databse'):
        g.database = Database(DATABASE)
        # マイグレーションが実行されていない場合はmigrate
        if not app.config['migrated'] and migrate(g.database, os.path.join(os.path.dirname(__file__), 'migration.json')):
            app.config['migrated'] = True
    return g.database


# Tables API 定義
@app.route('/tables', methods=['GET'])
def get_tables():
    ''' table列挙 '''
    db = get_db()
    return jres(200, db.get_tables())

@app.route('/tables/<string:name>', methods=['GET'])
def get_table(name):
    ''' tableスキーマ取得 '''
    db = get_db()
    res = db.get_table(name)
    if res == False:
        return jres(400, {
            'message': f'table "{name}" not exists'
        })
    return jres(200, res)

@app.route('/tables/<string:name>', methods=['POST'])
def create_table(name):
    ''' table作成 '''
    db = get_db()
    if db.create_table(name, request.json['columns']):
        return jres(201, {
            'message': f'table "{name}" created'
        })
    return jres(400, {
        'message': f'table "{name}" already exists'
    })

@app.route('/tables', methods=['DELETE'])
def drop_tables():
    ''' table全削除 '''
    db = get_db()
    db.drop_tables()
    return jres(200, {
        'message': 'all tables deleted'
    })

@app.route('/tables/<string:name>', methods=['DELETE'])
def drop_table(name):
    ''' table削除 '''
    db = get_db()
    if db.drop_table(name):
        return jres(200, {
            'message': f'table "{name}" deleted'
        })
    return jres(400, {
        'message': f'table "{name}" not exists'
    })


# Rows API 定義
@app.route('/tables/<string:name>/rows', methods=['GET'])
def get_rows(name):
    ''' tableにデータinsert '''
    db = get_db()
    res = db.get_rows(name, {} if request.json is None else request.json)
    if res == False:
        return jres(400, {
            'message': f'table "{name}" not exists'
        })
    return jres(200, res)

@app.route('/tables/<string:name>/rows', methods=['POST'])
def insert_rows(name):
    ''' tableにデータinsert '''
    db = get_db()
    res = db.insert_rows(name, request.json['values'])
    if res == False:
        return jres(400, {
            'message': f'table "{name}" not exists'
        })
    return jres(201, {
        'message': f'{res} rows inserted into table "{name}"'
    })


@app.route('/tables/<string:name>/rows', methods=['PUT'])
def update_rows(name):
    ''' tableのデータをupdate '''
    db = get_db()
    res = db.update_rows(name, request.json)
    if res == False:
        return jres(400, {
            'message': f'table "{name}" not exists'
        })
    return jres(200, {
        'message': f'{res} rows updated in table "{name}"'
    })

@app.route('/tables/<string:name>/rows', methods=['DELETE'])
def delete_rows(name):
    ''' tableのデータをdelete '''
    db = get_db()
    res = db.delete_rows(name, request.json)
    if res == False:
        return jres(400, {
            'message': f'table "{name}" not exists'
        })
    return jres(200, {
        'message': f'{res} rows deleted from table "{name}"'
    })


# Flaskサーバー実行
if __name__ == "__main__":
    # Databaseサーバーは localhost:5000 で実行
    app.run(debug=True, port=5000)
