# SQLite3 REST API Server

## Environments
- Python `3.6.7`
    - Flask `1.0.2`
        ```bash
        $ pip install flask
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
        curl -X POST -H 'Content-Type: application/json' -d '{
            "columns": [
                ["id", "int", {"primary_key":true}],
                ["user","str"]
            ]}' http://localhost:5000/tables/hoge
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
            "where": { // @optional: 条件式のポーランド記法配列
                /* operator:
                    "<" | "<=" | ">" | ">=" | "=" | "!=" | "and" | "or" | "like"
                */
                "<operator>": ["<expression>", ...],
                "<operator>": {"<column_name>": column_value, ...}
            },
            "order": { // @optional
                "<column_name>": "asc" or "desc", ...
            },
            "limit": 0 ~, // @optional
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
        curl -X GET -H 'Content-Type: application/json' -d '{
            "select": ["*"],
            "where": {
                "and": {
                    ">": {"id": 1},
                    "like": {"user": "%admin%"}
                }
            },
            "order": {"id": "desc"},
            "limit": 5}' http://localhost:5000/tables/users/rows
        ```
- POST:
    - `POST /tables/<table_name>/rows`
        ```javascript
        request: {
            "values": [
                ["<column1_name>", "<column2_name>", ...],
                ["<column1_val1>", "<column2_val1>", ...],
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
        # INSERT INTO users (user, password) VALUES (?, ?); | [["admin", "pass"], ["hoge", "fuga"]]
        curl -X POST -H 'Content-Type:application/json' -d '{
            "values":[
                ["user", "password"],
                ["admin", "pass"],
                ["hoge", "fuga"]
            ]}' http://localhost:5000/tables/users/rows
        ```
- PUT:
  - `PUT /tables/<table_name>/rows`
    ```javascript
    request: {
        "where": { // @optional
            "<operator>": ["<expression>", ...],
            "<operator>": {"<column_name>": column_value, ...},
        },
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
    curl -X PUT -H 'Content-Type:application/json' -d '{
        "values": {
            "user": "yoya"
        },
        "where": {
            "=": {"id": 1}
        }' http://localhost:5000/tables/users/rows
    ```
- DELETE:
  - `DELETE /tables/<table_name>/rows`
    ```javascript
    request: {
      "where": { // @optional
            "<operator>": ["<expression>", ...],
            "<operator>": {"<column_name>": column_value, ...},
        }
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
    curl -X DELETE -H 'Content-Type:application/json' -d '{
        "where": {
            "<=": {"id", 10}
        }' http://localhost:5000/tables/users/rows
    ```
