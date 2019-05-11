from flask import g, Flask, request
from api.tables import define_tables_api
from api.rows import define_rows_api
from pprint import pprint

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['database'] = 'database.sqlite3'

# Tables API 定義
define_tables_api(app, '/tables')

# Rows API 定義
define_rows_api(app, '/tables')

# Flaskサーバー実行
if __name__ == "__main__":
  app.run(debug=True)
