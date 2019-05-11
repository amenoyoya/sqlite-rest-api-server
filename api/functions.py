'''
functions for this module
'''

from sqlalchemy import create_engine, MetaData, Integer, String, Text, Float
from flask import g, jsonify

class Database:
  ''' SQLAlchemyデータベース '''
  types = {
    # Databse basic types
    'int': Integer, 'str': String, 'text': Text,  'num': Float 
  }

  def __init__(self, db_name):
    self.engine = create_engine('sqlite:///' + db_name)
    self.meta = MetaData(self.engine, reflect=True)


def jres(status_code, content):
  ''' ステータスコード付きでJsonレスポンス作成 '''
  res = jsonify(content)
  res.status_code = status_code
  return res


def get_db(app):
  ''' Databaseのconnectionを取得 '''
  if not hasattr(g, 'databse'):
    # flaskアプリケーションの設定['database']からデータベースを開く
    g.database = Database(app.config['database'])
  return g.database
