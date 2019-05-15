from ws import WebsocketClient

if __name__ == "__main__":
    ws = WebsocketClient()
    ws.open("ws://localhost:9999")
    ws.log("Open")
    ws.log("Sending 'Hellow, World'...")
    ws.send_message("Hello, World")
    ws.log("Sent")
    ws.log("Receiving...")
    result = ws.recieve_message()
    ws.log("Received '{}'".format(result))
    ws.close()