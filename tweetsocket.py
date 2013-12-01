from tornado import websocket, web, ioloop
import tornadoredis

c = tornadoredis.Client()
c.connect()
client_list = []


class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        if self not in client_list:
            client_list.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        if self in client_list:
            client_list.remove(self)


def on_message(m):
    if m.kind == "message":
        for client in client_list:
            client.write_message(m.body)


def on_subscribed(s):
    c.listen(on_message)


app = web.Application([
    (r'/tweetstream', SocketHandler),
])

app.listen(8888)
c.subscribe('tweets', callback=on_subscribed)
ioloop.IOLoop.instance().start()
