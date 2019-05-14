'''
Websocket ラッパークラス
'''
import logging
from websocket_server import WebsocketServer as create_server
from websocket import create_connection

def create_logger():
  ''' ロガー作成 '''
  handler = logging.StreamHandler()
  handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)
  return logger


class WebsocketServer:
  ''' Websocket Server ラッパークラス '''
  def __init__(self, port=3000, host='localhost'):
    self.server = create_server(port=port, host=host, loglevel=logging.INFO)
    self.server.set_fn_new_client(self.on_client_connected)
    self.server.set_fn_client_left(self.on_client_disconnected)
    self.server.set_fn_message_received(self.on_message_received)
    self.logger = create_logger()
  
  def log(self, msg, *args, **kargs):
    ''' ログメッセージを出力 '''
    self.logger.info(msg, *args, **kargs)

  def send_message(self, client, message):
    ''' clientにmessage送信 '''
    return self.server.send_message(client, message)

  def run_forever(self):
    ''' サーバー実行 '''
    return self.server.run_forever()

  # --- event methods --- #
  def on_client_connected(self, client, server):
    ''' 新規クライアントが接続したときのコールバック '''
    logger.info('New client {}:{} has been connected.'.format(client['address'][0], client['address'][1]))
  
  def on_client_disconnected(self, client, server):
    ''' クライアントとの接続が終了したときのコールバック '''
    logger.info('Client {}:{} has been disconnected.'.format(client['address'][0], client['address'][1]))
  
  def on_message_recieved(self, client, server, message):
    ''' クライアントからメッセージを受信したときのコールバック '''
    logger.info('Message "{}" has been received from {}:{}'.format(message, client['address'][0], client['address'][1]))


class WebsocketClient:
  ''' Websocket Client ラッパークラス '''
  def __init__(self):
    self.client = None
    self.logger = create_logger()

  def open(self, server_host):
    ''' server_hostにクライアントを新規接続 '''
    self.close()
    self.client = create_connection(server_host)
  
  def open_server(self, server_host):
    ''' server_hostにクライアントを新規接続し、サーバーとして動作させる '''
    self.close()
    websocket.enableTrace(False)
    self.client = websocket.WebSocketApp(
      server_host,
      on_message = self.on_message_recieved,
      on_error = self.on_error,
      on_close = self.on_disconnect
    )
    self.client.on_open = self.on_connect
    self.client.run_forever()
  
  def close(self):
    ''' clientをサーバーから切断する '''
    if self.client is not None:
      self.client.close()
      self.client = None

  def log(self, msg, *args, **kargs):
    ''' ログメッセージを出力 '''
    self.logger.info(msg, *args, **kargs)

  def send_message(self, message):
    ''' 接続先のサーバーにmessage送信 '''
    return self.client.send(message)
  
  def recieve_message(self):
    ''' 接続先サーバーから送られてきたメッセージを受信 '''
    return self.client.recv()

  # --- event methods (サーバーモードで動作する際に使用) --- #
  