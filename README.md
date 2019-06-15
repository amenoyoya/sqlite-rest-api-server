# SQLite3 REST API Server

## Environments
- Python `3.6.7`
    - Flask `1.0.2`
        ```bash
        $ pip install flask
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
    
    => response time: 0.28 s (in Windows)
    ```
- サーバー3層構造
    ```python
    client => 'localhost:4000' => 'localhost:5000':
        'localhost:4000': 前処理用APサーバー
        'localhost:5000': SQLite操作APサーバー
    
    => response time: 1.28 s (in Windows)
    => response time: 0.04 s (in Ubuntu)
    ```

#### Conclusion
Windows環境のサーバーは遅い

サーバーはLinux環境に限る
