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
    ```json
    response: {
      "status": 200,
      "data": {
        "tables": {
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
    ```json
    response: {
      "status": 200,
      "data": {
        "table": [
          {
            "name": "<column_name>",
            "type": "<column_type>",
            "nullable": true/false,
            "primary_key": true/false
          },
          ...
        ]
      }
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
    ```json
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
    curl -X POST -H 'Content-Type:application/json' -d '{"columns":[["id","int",{"primary_key":true,"autoincrement":true}],["user","str"]]}' http://localhost:5000/tables/hoge
    ```
- DELETE:
  - `DELETE /tables`
    ```json
    response: {
      "status": 200,
      "data": {
        "message": "all tables deleted"
      }
    }
    ```
  - `DELETE /tables/<table_name>`
    ```json
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