from flask import g, Flask, request
from api.tables import define_tables_api
from api.rows import define_rows_api
import os

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['database'] = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

# Tables API 定義
define_tables_api(app, '/tables')

# Rows API 定義
define_rows_api(app, '/tables')

# Flaskサーバー実行
if __name__ == "__main__":
  # Databaseサーバーは localhost:5000 で実行
  app.run(debug=True, port=5000)
