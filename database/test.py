# encoding: utf-8
from lib.sqldb import SqlDB

db = SqlDB('test.db')
print(db.get_tables())

'''
db.cursor.execute('create table if not exists users (id integer primary key autoincrement, email varchar, password varchar)')
db.cursor.execute('pragma table_info("users")')
print(
    [dict(row) for row in db.cursor.fetchall()]
)
'''
