'''
Databaseサーバー（Websocket版）
'''

from lib.db import Database
from lib.ws import WebsocketServer
import os, json

# 使用するデータベース
DATABASE = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

class DatabaseWebsocketServer(WebsocketServer):
    ''' DatabaseWebsocketサーバー '''
    def __init__(self, db_name, port=3000, host='localhost'):
        super(DatabaseWebsocketServer, self).__init__(port, host)
        self.database = Database(db_name)

    def migrate(self, migration):
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
            self.database.drop_tables()
        # table構築
        if not isinstance(tables, dict):
            return False
        for table, columns in tables.items():
            if self.database.is_table_exists(table):
                continue
            # 存在しないtableを構築し、データ流し込み
            if self.database.create_table(table, columns) == False:
                return False
            rows = values.get(table) if isinstance(values, dict) else None
            if rows and self.database.insert_rows(table, rows) == False:
                return False
        return True

    def on_message_recieved(self, client, message):
        ''' メッセージ受信イベント '''
        # tables API: tables://{json}
        ## json: {method: "GET|POST|PUT|DELETE", table@optional: "target_table", ...}
        if message[:9] == 'tables://':
            data = json.loads(message[9:])
            if isinstance(data, dict):
                self.send_message(self._switch_tables_api(data))
            else:
                self.send_message('invalid json data')
        # rows API: rows://{json}
        ## json: {method: "GET|POST|PUT|DELETE", table: "target_table", ...}
        elif message[:7] == 'rows://':
            data = json.loads(message[7:])
            if isinstance(data, dict):
                self.send_message(self._switch_rows_api(data))
            else:
                self.send_message('invalid json data')
    
    def _switch_tables_api(self, data):
        ''' JSONデータから tables API 振り分け '''
        method = data.get('method')
        table = data.get('table')
        if method == 'GET':
            if isinstance(table, str):
                return self.get_table(table, data)
            else:
                return self.get_tables(data)
        elif method == 'POST':
            if isinstance(table, str):
                return self.create_table(table, data)
            else:
                return 'target table to create not found'
        elif method == 'DELETE':
            if isinstance(table, str):
                return self.drop_table(table, data)
            else:
                return self.drop_tables(data)
        return 'unknown method: tables api supported methods GET, POST, DELETE'

    def _switch_rows_api(self, data):
        ''' JSONデータから rows API 振り分け '''
        method = data.get('method')
        table = data.get('table')
        
        if not isinstance(table, str):
            return 'target table for rows api not found'
        
        if method == 'GET':
            return self.get_rows(table, data)
        elif method == 'POST':
            return self.insert_rows(table, data)
        elif method == 'PUT':
            return self.update_rows(table, data)
        elif method == 'DELETE':
            return self.delete_rows(table, data)
        return 'unknown method: tables api supported methods GET, POST, PUT, DELETE'
    
    # Tables API 定義
    def get_tables(self, data):
        ''' table列挙 '''
        return json.dumps(self.database.get_tables())

    def get_table(self, name, data):
        ''' tableスキーマ取得 '''
        res = self.database.get_table(name)
        if res == False:
            return f'table "{name}" not exists'
        return json.dumps(res)

    def create_table(self, name, data):
        ''' table作成 '''
        if self.database.create_table(name, data.get('columns')):
            return f'table "{name}" created'
        return  f'table "{name}" already exists'

    def drop_tables(self, data):
        ''' table全削除 '''
        self.database.drop_tables()
        return 'all tables deleted'

    def drop_table(self, name, data):
        ''' table削除 '''
        if self.database.drop_table(name):
            return f'table "{name}" deleted'
        return f'table "{name}" not exists'


    # Rows API 定義
    def get_rows(self, name, data):
        ''' tableにデータinsert '''
        res = self.database.get_rows(name, {} if data is None else data)
        if res == False:
            return f'table "{name}" not exists'
        return json.dumps(res)

    def insert_rows(self, name, data):
        ''' tableにデータinsert '''
        res = self.database.insert_rows(name, data.get('values'))
        if res == False:
            return f'table "{name}" not exists'
        return f'{res} rows inserted into table "{name}"'

    def update_rows(self, name, data):
        ''' tableのデータをupdate '''
        res = self.database.update_rows(name, data)
        if res == False:
            return f'table "{name}" not exists'
        return f'{res} rows updated in table "{name}"'

    def delete_rows(self, name, data):
        ''' tableのデータをdelete '''
        res = self.database.delete_rows(name, data)
        if res == False:
            return f'table "{name}" not exists'
        return f'{res} rows deleted from table "{name}"'


# Websocketサーバー実行
if __name__ == "__main__":
    # Databaseサーバーは localhost:5000 で実行
    ws = DatabaseWebsocketServer(DATABASE, port=5000)
    ws.run_forever()
