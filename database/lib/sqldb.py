# encoding: utf-8
'''
SQLite3 wrapping for REST API
'''
import sqlite3, re

class Variable:
    ''' 変数名として使える文字列か判定するクラス '''
    class NameError(Exception):
        def __str__(self):
            return 'Invalid character specified for variable name.'
    
    # 変数名にはアルファベット, 数字, アンダーバーのみ使用可能
    pattern = re.compile('^[a-zA-Z0-9_]+$')
    
    def __init__(self, variable_name):
        # '*'は許可
        if variable_name == '*':
            self.name = variable_name
        else:
            if Variable.pattern.match(variable_name) is None:
                raise Variable.NameError()
            self.name = variable_name
    
    def __str__(self):
        return self.name


class SqlDB:
    ''' SQLite wrapper class '''
    types = {
        # Databse basic types
        'int': 'integer', 'str': 'varchar', 'text': 'text',  'num': 'number' 
    }

    # --- private methods --- #
    def _get_table_schema(self, table_name):
        ''' tableスキーマ取得 '''
        self.cursor.execute('pragma table_info("%s")' % (table_name))
        return [
            {
                'name': row['name'],
                'type': row['type'],
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
        if self.is_table_exists(table_name):
            return self._get_table_schema(table_name)
        return False

    def create_table(self, table_name, columns):
        ''' table作成
        params:
            table_name (str): target table name
            columns (list): [
                [
                    column_name,
                    column_type, # "int" | "str" | "text" | "num"
                    { # @optional
                        "primary_key": True/False, # integerでprimary_keyならautoincrementされる
                        "nullable": True/False,
                    }
                ],
                ...
            ]
        returns:
            if table already exists: False
            else: True
        '''
        if self.is_table_exists(table_name):
            return False
        cols = []
        for column in columns:
            opt = {
                'nullable': '' if column[2].get('nullable') else ' not null',
                'primary_key': ' primary key' if column[2].get('primary_key') else ''
            } if len(column) > 2 else {
                'nullable': '',
                'primary_key': ''
            }
            cols += [str(Variable(column[0])) + ' ' + SqlDB.types[column[1]] + opt['nullable'] + opt['primary_key']]
        self.cursor.execute('create table ' + str(Variable(table_name)) + ' (' + ','.join(cols) + ')')
        self.tables += [table_name]
        return True

    def drop_tables(self):
        ''' table全削除 '''
        for table in self.tables:
            self.cursor.execute('drop table ' + table)
        self.tables = []

    def drop_table(self, table_name):
        ''' table削除
        params:
            table_name (str): target table name
        returns:
            if table not exists: False
            else: True
        '''
        if not self.is_table_exists(table_name):
            return False
        self.cursor.execute('drop table ' + table_name)
        self.tables.remove(table_name)
        return True
