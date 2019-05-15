from ws import WebsocketClient
import _thread, time

class MyClient(WebsocketClient):
    def on_connect(self):
        def run(*args):
            ws.log('Open')
            for i in range(3):
                time.sleep(1)
                message = "Hello " + str(i)
                self.send_message(message)
                self.log('Sent:{}'.format(message))
                time.sleep(1)
            self.close()
        _thread.start_new_thread(run, ())

if __name__ == "__main__":
    ws = MyClient()
    ws.open_server('ws://localhost:12345')
