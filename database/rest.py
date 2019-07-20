# encoding: utf-8
'''
Database REST API Server

Copyright (C) 2019 yoya(@amenoyoya). All rights reserved.
GitHub: https://github.com/amenoyoya/sqlite-rest-api-server
License: MIT License
'''
from pylib.web.frasco import g, request, Frasco, Response
from pylib.sqldb import SqlDB
import os, json

# 使用するデータベース
DATABASE = os.path.join(os.path.dirname(__file__), 'database.sqlite3')
# 使用するマイグレーションファイル
MIGRATION = os.path.join(os.path.dirname(__file__), 'migration.json')

# Flaskアプリケーション
app = Frasco(__name__)
app.config['migrated'] = False # migration実行フラグ

def get_db():
    ''' Databaseのconnectionを取得 '''
    if not hasattr(g, 'databse'):
        g.database = SqlDB(DATABASE)
        # マイグレーションが実行されていない場合はmigrate
        if not app.config['migrated'] and os.path.exists(MIGRATION):
            with open(MIGRATION, 'rb') as f:
                if g.database.migrate(json.load(f)):
                    app.config['migrated'] = True # マイグレーション実行済みに
    return g.database

# Tables API 定義
@app.get('/tables')
def get_tables():
    ''' table列挙 '''
    return Response.json(get_db().get_tables())

@app.get('/tables/<string:name>')
def get_table(name):
    ''' tableスキーマ取得 '''
    res = get_db().get_table(name)
    if res == False:
        return Response.json({
            'message': f'table "{name}" not exists'
        }, 400)
    return Response.json(res)

@app.post('/tables/<string:name>')
def create_table(name):
    ''' table作成 '''
    if get_db().create_table(name, request.json['columns']):
        return Response.json({
            'message': f'table "{name}" created'
        }, 201)
    return Response.json({
        'message': f'table "{name}" already exists'
    }, 400)

@app.delete('/tables')
def drop_tables():
    ''' table全削除 '''
    get_db().drop_tables()
    return Response.json({
        'message': 'all tables deleted'
    })

@app.delete('/tables/<string:name>')
def drop_table(name):
    ''' table削除 '''
    if get_db().drop_table(name):
        return Response.json({
            'message': f'table "{name}" deleted'
        })
    return Response.json({
        'message': f'table "{name}" not exists'
    }, 400)

# Rows API 定義
@app.get('/tables/<string:name>/rows')
def get_rows(name):
    ''' tableにデータinsert '''
    res = get_db().get_rows(name, {} if request.json is None else request.json)
    if res == False:
        return Response.json({
            'message': f'table "{name}" not exists'
        }, 400)
    return Response.json(res)

@app.post('/tables/<string:name>/rows')
def insert_rows(name):
    ''' tableにデータinsert '''
    res = get_db().insert_rows(name, request.json['values'])
    if res == False:
        return Response.json({
            'message': f'table "{name}" not exists'
        }, 400)
    return Response.json({
        'message': f'{res} rows inserted into table "{name}"'
    }, 201)

@app.put('/tables/<string:name>/rows')
def update_rows(name):
    ''' tableのデータをupdate '''
    res = get_db().update_rows(name, request.json)
    if res == False:
        return Response.json({
            'message': f'table "{name}" not exists'
        }, 400)
    return Response.json({
        'message': f'{res} rows updated in table "{name}"'
    })

@app.delete('/tables/<string:name>/rows')
def delete_rows(name):
    ''' tableのデータをdelete '''
    res = get_db().delete_rows(name, request.json)
    if res == False:
        return Response.json({
            'message': f'table "{name}" not exists'
        }, 400)
    return Response.json({
        'message': f'{res} rows deleted from table "{name}"'
    })

# Flaskサーバー実行
if __name__ == "__main__":
    # Databaseサーバーは localhost:5000 で実行
    app.run(debug=True, port=5000)
