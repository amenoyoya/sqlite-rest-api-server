'''
Websocket版curlのようなもの
'''
from database.lib.ws import WebsocketClient
import sys

def main():
    if len(sys.argv) < 3:
        print('Usage: wscurl <websocket_host> <api_string>')
        print('\tapi_string: "tables://{json_data}" or "rows://{json_data}"')
        return 1
    ws = WebsocketClient()
    ws.open(sys.argv[1])
    ws.send_message(sys.argv[2])
    print(ws.recieve_message())
    return 0

if __name__ == "__main__":
    main()