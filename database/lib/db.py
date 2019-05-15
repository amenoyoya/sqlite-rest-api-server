'''
Databaseラッパークラス
'''

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Float
from sqlalchemy.sql import insert, select, update, delete, and_, or_, tuple_, asc, desc
from .rpn import RPN

# --- private functions --- #
def _get_table_schema(table):
    ''' tableスキーマ取得 '''
    return [{
        'name': c.name,
        'type': c.type.python_type.__name__,
        'nullable': c.nullable,
        'primary_key': c.primary_key
    } for c in table.columns]

def _build_where(table, where_rpn):
    ''' selectのwhere句のクエリを作成
    where_rpn (list): [column, value, operator, ...]
        => Reverse Polish Notation
        (el.) WHERE id <= 5 AND user LIKE "%admin%"
            => ["id", 5, "<=", "user", "%admin%", "like", "and"]
    '''
    # 演算子定義
    op = {
        '<': lambda x, y: x < y, '<=': lambda x, y: x <= y,
        '>': lambda x, y: x > y, '>=': lambda x, y: x >= y,
        '=': lambda x, y: x == y, '!=': lambda x, y: x != y,
        'and': lambda x, y: and_(x, y), 'or': lambda x, y: or_(x, y),
        'like': lambda x, y: x.like(y), 'in': lambda x, y: tuple_(x).in_([(e,) for e in y]),
    }
    # 変数定義
    op.update(table.columns)
    # 逆ポーランド記法でクエリ生成
    return RPN(where_rpn, op)[0]

def _build_order_by(query, table, orders):
    ''' selectのorder_by句のクエリを作成 '''
    for order in orders:
        if order[0] == 'asc':
            query = query.order_by(asc(table.columns[order[1]]))
        elif order[0] == 'desc':
            query = query.order_by(desc(table.columns[order[1]]))
    return query

def _build_query(query, table, json, is_select=False):
    ''' jsonの内容からクエリを生成 '''
    # where
    if 'where' in json:
        query = query.where(_build_where(table, json['where']))
    # order_by (select only)
    if is_select and 'order_by' in json:
        query = _build_order_by(query, table, json['order_by'])
    # limit (select only)
    if is_select and 'limit' in json:
        query = query.limit(json['limit'])
    return query


class Database:
    ''' SQLAlchemyデータベースラッパークラス '''
    types = {
        # Databse basic types
        'int': Integer, 'str': String, 'text': Text,  'num': Float 
    }

    def __init__(self, db_name):
        self.engine = self.meta = None
        self.create(db_name)
    
    def create(self, db_name):
        self.destroy()
        self.engine = create_engine('sqlite:///' + db_name)
        self.meta = MetaData(self.engine, reflect=True)

    def destroy(self):
        if self.engine is not None:
            self.engine.dispose()
            self.engine = self.meta = None
    
    def is_table_exists(self, table_name):
        ''' テーブルの存在確認 '''
        return table_name in self.meta.tables

    def connect(self):
        ''' データベースにアタッチ '''
        return self.engine.connect()

    # --- methods for tables managiment --- #
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
            table: _get_table_schema(self.meta.tables[table]) for table in self.meta.tables
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
