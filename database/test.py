# encoding: utf-8
from lib.db import Database

db = Database('config.db')
print(db.get_rows('users', {
    'select': ['*'],
    'where': ['user_id', 'UFT9JKF34', '=']
}))
