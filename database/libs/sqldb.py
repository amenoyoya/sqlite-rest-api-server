# encoding: utf-8
'''
SQLite3 wrapping for REST API

Copyright (C) 2019 yoya(@amenoyoya). All rights reserved.
GitHub: https://github.com/amenoyoya/sqlite-rest-api-server
License: MIT License
'''
import sqlite3
from .query import Variable, QueryBuilder

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
            cols += [Variable(column[0]).value + ' ' + SqlDB.types[column[1]] + opt['nullable'] + opt['primary_key']]
        self.cursor.execute('create table ' + Variable(table_name).value + ' (' + ','.join(cols) + ')')
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

    # --- methods for rows managiment --- #
    def get_rows(self, table_name, conditions={}):
        ''' table内のデータselect
        params:
            table_name (str): target table name
            conditions (dict): {
                "select": ["*" or column_name, ...],
                "where": {operator: [exp, ...], operator: {column_name: value}},
                "order": {column: 'desc' or 'asc'}
                "limit": 0 ~
            }
        returns:
            if table not exists: False
            else: list [
                {column_name: column_value, ...},
                ...
            ]
        '''
        if not self.is_table_exists(table_name):
            return False
        query = QueryBuilder.build_select_query(conditions.get('select')) + ' from ' + table_name
        where, binds = QueryBuilder.build_where_query(conditions.get('where'))
        query += ' ' + where
        query += ' ' + QueryBuilder.build_order_query(conditions.get('order'))
        limit = conditions.get('limit')
        if type(limit) is int:
            query += ' limit ' + str(limit)
        cursor = self.cursor.execute(query, binds)
        return [dict(row) for row in cursor.fetchall()]

    def insert_rows(self, table_name, values):
        ''' tableにデータinsert
        params:
            table_name (str): target table name
            values (list): [
                [column1_name, column2_name, ...],
                [column1_value1, column2_value1, ...],
                [column1_value2, column2_value2, ...],
                ...
            ]
        returns:
            if table not exists: False
            else: inserted row count (int)
        '''
        if not self.is_table_exists(table_name):
            return False
        query, binds = QueryBuilder.build_insert_query(table_name, values)
        cursor = self.cursor.executemany(query, binds)
        self.connect.commit() # 変更を反映
        return cursor.rowcount

    def update_rows(self, table_name, conditions):
        ''' tableのデータをupdate
        params:
            table_name (str): target table name
            conditions (dict): {
                "values": {column_name: column_value, ...},
                "where": {operator: [exp, ...], operator: {column_name: value}}
            }
        returns:
            if table not exists: False
            else: updated row count (int)
        '''
        if not self.is_table_exists(table_name):
            return False
        query, binds = QueryBuilder.build_update_query(table_name, conditions.get('values'))
        where, _binds = QueryBuilder.build_where_query(conditions.get('where'))
        binds += _binds
        result = self.cursor.execute(query + ' ' + where, binds)
        self.connect.commit() # 変更を反映
        return result.rowcount

    def delete_rows(self, table_name, conditions):
        ''' tableのデータをdelete
        params:
            table_name (str): target table name
            conditions (dict): {
                "where": {operator: [exp, ...], operator: {column_name: value}}
            }
        returns:
            if table not exists: False
            else: deleted row count (int)
        '''
        if not self.is_table_exists(table_name):
            return False
        where, binds = QueryBuilder.build_where_query(conditions.get('where'))
        query = 'delete from ' + table_name + ' ' + where
        print(query, binds)
        result = self.cursor.execute(query, binds)
        self.connect.commit() # 変更を反映
        return result.rowcount
