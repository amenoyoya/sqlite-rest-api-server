# encoding: utf-8
'''
SQLite3 wrapping for REST API
'''
import sqlite3
from inspect import signature

def RPN(exp, op):
    ''' 逆ポーランド記法を計算する関数
    params:
        exp list: 逆ポーランド記法プログラムの配列（el. [1, 2, '+'] => 1 + 2）
        op dict: 演算子,変数の定義（el. {'+': (lambda x, y: x + y), 'ten': 10}）
    '''
    stack = []
    for e in exp:
        f = None if isinstance(e, list) else op.get(e)
        if f is None:
            # 演算子でも変数でもない場合はstack
            stack.append(e)
        elif callable(f):
            # 演算子なら演算実行
            argc = len(signature(f).parameters) # 関数の引数の数を取得
            res = f(*stack[-argc:]) # stackの後ろから引数を取得し、関数実行
            stack = stack[:-argc] # 引数分をstackから削除
            if res is not None:
                stack.append(res) # 関数の戻り値をstack
        else:
            # 変数の値をstack
            stack.append(f)
    return stack


class SqlDB:
    ''' SQLite wrapper class '''
    types = {
        # Databse basic types
        'int': 'integer', 'str': 'varchar', 'text': 'text',  'num': 'number' 
    }
    sqltypes = {
        'integer': 'int', 'varchar': 'str', 'text': 'text',  'number': 'num'
    }

    # --- private methods --- #
    def _get_table_schema(self, table_name):
        ''' tableスキーマ取得 '''
        self.cursor.execute('pragma table_info("%s")' % (table_name))
        return [
            {
                'name': row['name'],
                'type': row['type'],
                'default': row['dflt_value'],
                'nullable': row['notnull'] == 0,
                'primary_key': row['pk'] == 1
            } for row in self.cursor.fetchall()
        ]

    # --- normal methods --- #
    def __init__(self, db_name):
        self.connect = None
        self.open(db_name)
    
    def __del__(self):
        self.close()
    
    def open(self, db_name):
        ''' データベースに接続 '''
        self.close()
        self.connect = sqlite3.connect(db_name)
        self.connect.row_factory = sqlite3.Row # fetchデータをdict形式で取得
        self.cursor = self.connect.cursor()
        # table列挙
        self.cursor.execute('select * from sqlite_master where type="table"')
        self.tables = [row[1] for row in self.cursor.fetchall()]

    def close(self):
        ''' データベースから切断 '''
        if self.connect is not None:
            self.connect.close()
            self.connect = self.cursor = self.tables = None
    
    def is_table_exists(self, table_name):
        ''' テーブルの存在確認 '''
        return table_name in self.tables

    # --- methods for tables management --- #
    def get_tables(self):
        ''' table列挙
        returns:
            {table_name: [
                {
                    "name": column_name, "type": column_type, "nullable": True/False, "primary_key": True/False
                },
                ...
            ], ...}
        '''
        return {
            table: self._get_table_schema(table) for table in self.tables
        }

    def get_table(self, table_name):
        ''' tableスキーマ取得
        params:
            table_name (str): target table name
            returns:
            if table not exists: False
            else: dict {
                "name": column_name, "type": column_type, "nullable": True/False, "primary_key": True/False
            }
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        return _get_table_schema(table)

    def create_table(self, table_name, columns):
        ''' table作成
        params:
            table_name (str): target table name
            columns (list): [
                [
                    column_name,
                    column_type, # "int" | "str" | "text" | "num"
                    { # @optional
                        "primary_key": True/False,
                        "nullable": True/False, 
                        "autoincrement": True/False
                    }
                ],
                ...
            ]
        returns:
            if table already exists: False
            else: True
        '''
        if table_name in self.meta.tables:
            return False
        columns = [
            Column(column[0], Database.types[column[1]], **column[2] if len(column) > 2 else {})
            for column in columns
        ]
        Table(table_name, self.meta, *columns).create()
        return True

    def drop_tables(self):
        ''' table全削除 '''
        self.meta.drop_all()

    def drop_table(self, table_name):
        ''' table削除
        params:
            table_name (str): target table name
        returns:
            if table not exists: False
            else: True
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        table.drop()
        return True

    # --- methods for rows managiment --- #
    def get_rows(self, table_name, conditions):
        ''' table内のデータselect
        params:
            table_name (str): target table name
            conditions (dict): {
                "select": ["*" or column_name, ...],
                "where": @where_rpn,
                "order_by": [["asc"/"desc", column_name], ...],
                "limit": 0 ~
            }
        returns:
            if table not exists: False
            else: list [
                {column_name: column_value, ...},
                ...
            ]
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        with self.connect() as con:
            selects = conditions.get('select')
            query = select(
                [table] if selects is None \
                else [table if s == '*' else table.columns[s] for s in selects]
            )
            result = con.execute(_build_query(query, table, conditions, True))
            return [{key: val for key, val in row.items()} for row in result]

    def insert_rows(self, table_name, values):
        ''' tableにデータinsert
        params:
            table_name (str): target table name
            values (list): [
                {column_name: column_value, ...},
                ...
            ]
        returns:
            if table not exists: False
            else: inserted row count (int)
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        with self.connect() as con:
            result = con.execute(insert(table, values=values))
            return result.rowcount

    def update_rows(self, table_name, conditions):
        ''' tableのデータをupdate
        params:
            table_name (str): target table name
            conditions (dict): {
                "values": {column_name: column_value, ...},
                "where": @where_rpn
            }
        returns:
            if table not exists: False
            else: updated row count (int)
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        with self.connect() as con:
            result = con.execute(
                _build_query(update(table), table, conditions),
                **conditions['values']
            )
            return result.rowcount

    def delete_rows(self, table_name, conditions):
        ''' tableのデータをdelete
        params:
            table_name (str): target table name
            conditions (dict): {
                "where": @where_rpn
            }
        returns:
            if table not exists: False
            else: deleted row count (int)
        '''
        table = self.meta.tables.get(table_name)
        if table is None:
            return False
        with self.connect() as con:
            result = con.execute(
                _build_query(delete(table), table, conditions)
            )
            return result.rowcount
