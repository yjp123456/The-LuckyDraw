# -*- coding:utf8 -*-

import threading
import hashlib
import socket
import json
import base64
import struct

global clients
clients = {}
HOST = 'localhost'
PORT = 3002
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"


# 通知客户端
def notify(afid):
    for connection in clients.values():
        try:
            send_data(connection, json.dumps({
                "eventName": "__AFID",
                "data": {
                    "AFID": afid
                }
            }))
        except Exception, e:
            print e.message


def send_data(socket, data):
    #根据发送数据长度是否超过 125 ， 0xFFFF(65535) 来生成 1 个或 3 个或 9 个字节，来代表数据长度
    if data:
        data = str(data)
    else:
        return False
    token = "\x81"
    length = len(data)
    if length < 126:
        token += struct.pack("B", length)#B->unsigned char,表示把length转成一个字节
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)#H->unsigned short，表示把126转成一个字节，length转成2个字节
    else:
        token += struct.pack("!BQ", 127, length)#Q->unsigned long long，表示把127转成一个字节，length转成8个字节
    #!表示我们要使用网络字节顺序解析
    # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
    data = '%s%s' % (token, data)#token代表结构体Header
    socket.send(data)


# 客户端处理线程
class websocket_thread(threading.Thread):
    def __init__(self, connection, username):
        super(websocket_thread, self).__init__()
        self.connection = connection
        self.username = username

    def run(self):
        print 'new websocket client joined!'
        headers = {}
        shake = self.connection.recv(1024)

        if not len(shake):
            return False

        header, data = shake.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, val = line.split(': ', 1)
            headers[key] = val

        if 'Sec-WebSocket-Key' not in headers:
            print ('This socket is not websocket, client close.')
            self.connection.close()
            return False

        sec_key = headers['Sec-WebSocket-Key']
        res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

        str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ':' + str(PORT))
        print str_handshake
        self.connection.send(str_handshake)


# 服务端
class websocket_server(threading.Thread):
    def __init__(self):
        super(websocket_server, self).__init__()

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((HOST, PORT))
            sock.listen(5)
            print 'websocket server started!'
            while True:
                connection, address = sock.accept()
                try:
                    username = "ID" + str(address[1])
                    thread = websocket_thread(connection, username)
                    thread.start()
                    clients[username] = connection
                except Exception, e:
                    print e.message

        except Exception, e:
            print e.message


if __name__ == '__main__':
    server = websocket_server()
    server.start()
