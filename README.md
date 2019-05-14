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
  - websocket-server `0.4`
    ```bash
    $ pip install websocket-server

    # latest version update
    $ pip install --upgrade git+https://github.com/Pithikos/python-websocket-server
    ```
  - websocket-server `0.56.0`
    ```bash
    $ pip install websocket-client
    ```

***

## SQLite3 REST API
see [database/README.md](./database/README.md)

***

## Test

- サーバー2層構造
  ```python
  client => 'localhost:5000':
    'localhost:5000': SQLite操作APサーバー
  
  => response time: 0.28 s
  ```
- サーバー3層構造
  ```python
  client => 'localhost:4000' => 'localhost:5000':
    'localhost:4000': 前処理用APサーバー
    'localhost:5000': SQLite操作APサーバー
  
  => response time: 1.28 s
  ```
