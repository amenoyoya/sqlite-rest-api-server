from flask import Flask
from api.tables import define_tables_api

# Flaskアプリケーション
app = Flask(__name__)
app.config.from_object(__name__)
app.config['database'] = 'database.sqlite3'

# Tables API 定義
define_tables_api(app, '/tables')

# Flaskサーバー実行
if __name__ == "__main__":
  app.run(debug=True)
