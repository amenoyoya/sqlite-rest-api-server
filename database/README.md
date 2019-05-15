# SQLite3 REST API Server

## Environments
- Python `3.6.7`
    - Flask `1.0.2`
        ```bash
        $ pip install flask
        ```
    - SQLAlchemy `1.3.3`
        ```bash
        $ pip install sqlalchemy
        ```

***

## API

### API for tables
- GET:
    - `GET /tables`
        ```javascript
        response: {
            "status": 200,
            "data": {
                {
                    "<table_name>": [
                        {
                            "name": "<column_name>",
                            "type": "<column_type>",
                            "nullable": true/false,
                            "primary_key": true/false
                        },
                        ...
                    ],
                    ...
                }
            }
        }
        ```
    - `GET /tables/<table_name>`
        ```javascript
        response: {
            "status": 200,
            "data": [
                {
                    "name": "<column_name>",
                    "type": "<column_type>",
                    "nullable": true/false,
                    "primary_key": true/false
                },
                ...
            ]
        } or {
            "status": 400,
            "data": {
                "message": "table <table_name> not exists"
            }
        }
        ```
    - example:
        ```bash
        curl -X GET http://localhost:5000/tables
        ```
- POST:
    - `POST /tables/<table_name>`
        ```javascript
        request: {
            "columns": [
                [
                    "<column_name>",
                    "<column_type>", // int | str | text | num
                    { // @optional
                        "nullable": true/false,
                        "primary_key": true/false,
                        "autoincrement": true/false
                    }
                ],
                ...
            ]
        }
        response: {
            "status": 201 or 400,
            "data": {
                "message": "table <table_name> created"
                or "table <table_name> already exists"
            }
        }
        ```
    - example:
        ```bash
        curl -X POST -H 'Content-Type:application/javascript' -d '{"columns":[["id","int",{"primary_key":true,"autoincrement":true}],["user","str"]]}' http://localhost:5000/tables/hoge
        ```
- DELETE:
    - `DELETE /tables`
        ```javascript
        response: {
            "status": 200,
            "data": {
                "message": "all tables deleted"
            }
        }
        ```
    - `DELETE /tables/<table_name>`
        ```javascript
        response: {
            "status": 200,
            "data": {
                "message": "table <table_name> deleted"
            }
        }
        ```
    - example:
        ```bash
        curl -X DELETE http://localhost:5000/tables/hoge
        ```

---

### API for rows
- GET:
    - `GET /tables/<table_name>/rows`
        ```javascript
        request: {
            "select": [ //@optional
                "*" or "<column_name>"
            ],
            "where": [ // @optional: 条件式の逆ポーランド記法配列
                /* operators */
                '<': lambda x, y: x < y, '<=': lambda x, y: x <= y,
                '>': lambda x, y: x > y, '>=': lambda x, y: x >= y,
                '=': lambda x, y: x == y, '!=': lambda x, y: x != y,
                'and': lambda x, y: and_(x, y), 'or': lambda x, y: or_(x, y),
                'like': lambda x, y: x.like(y), 'in': lambda x, y: tuple_(x).in_([(e,) for e in y]),
            ],
            "order_by": [ // @optional
                ["asc" or "desc", "<column_name>"], ...
            ],
        "limit": 0～, // @optional
        }
        response: {
            "status": 200,
            "data": [
                {"<column_name>": column_value, ...},
                ...
            ]
        } or {
            "status": 400,
            "data": {
                "message": "table <table_name> not exists"
            }
        }
        ```
    - example:
        ```bash
        # SELECT * FROM users WHERE id > 1 AND user LIKE "%admin%" ORDER BY id DESC LIMIT 5;
        curl -X GET -H 'Content-Type:application/json' -d '{"select": ["*"], "where": ["id", 1, ">", "user", "%admin%", "like", "and"], "order_by": [["desc", "id"]], "limit": 5}' http://localhost:5000/tables/users/rows
        ```
- POST:
    - `POST /tables/<table_name>/rows`
        ```javascript
        request: {
            "values": [
                {"<column_value>": column_value, ...},
                ...
            ]
        }
        response: {
            "status": 201 or 400,
            "data": {
                "message": "<rows_count> rows inserted into table <table_name>"
                or "table <table_name> not exists"
            }
        }
        ```
    - example:
        ```bash
        curl -X POST -H 'Content-Type:application/javascript' -d '{"values":[{"user":"admin","password":"pass"},{"user":"hoge","password":"fuga"}]}' http://localhost:5000/tables/users/rows
        ```
- PUT:
  - `PUT /tables/<table_name>/rows`
    ```javascript
    request: {
      "where": @optional where::RPN,
      "values": {"<column_value>": column_value, ...}
    }
    response: {
      "status": 200 or 400,
      "data": {
        "message": "<rows_count> rows updated in table <table_name>"
          or "table <table_name> not exists"
      }
    }
    ```
  - example:
    ```bash
    # UPDATE users SET user = "yoya" WHERE id = 1;
    curl -X PUT -H 'Content-Type:application/javascript' -d '{"values":{"user":"yoya"},"where":["id",1,"="]}' http://localhost:5000/tables/users/rows
    ```
- DELETE:
  - `DELETE /tables/<table_name>/rows`
    ```javascript
    request: {
      "where": @optional where::RPN,
    }
    response: {
      "status": 200 or 400,
      "data": {
        "message": "<rows_count> rows deleted from table <table_name>"
          or "table <table_name> not exists"
      }
    }
    ```
  - example:
    ```bash
    # DELETE FROM users WHERE id <= 10;
    curl -X DELETE -H 'Content-Type:application/javascript' -d '{"where":["id",10,"<="]}' http://localhost:5000/tables/users/rows
    ```
