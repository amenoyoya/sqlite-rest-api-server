from ws import WebsocketServer
 
class MyServer(WebsocketServer):
    def on_message_recieved(self, client, message):
        self.log('Message "{}" has been received from {}:{}'.format(message, client['address'][0], client['address'][1]))
        reply_message = 'Hi! ' + message
        self.send_message(client, reply_message)
        self.log('Message "{}" has been sent to {}:{}'.format(reply_message, client['address'][0], client['address'][1]))

if __name__ == "__main__":
    server = MyServer(port=12345)
    server.run_forever()