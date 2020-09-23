import asyncio


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


class ClientServerProtocol(asyncio.Protocol):
    metric = {}

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')

    def data_received(self, data):
        message = data.decode()
        data = self.delegating(message)
        self.transport.write(data.encode())

    def delegating(self, message):
        try:
            message = message.replace('\n\n', '\n')
            status, payload = message.replace('\n', ' ').split(" ", 1)
            status, payload = status.strip(), payload

            if status == 'put' and payload.strip():
                rez = self.put(payload)
                return rez

            elif status == 'get' and payload.strip():
                res = self.get(payload)
                return res

            else:
                return 'error\nwrong command\n\n'

        except:
            return 'error\nwrong command\n\n'

    def put(self, payload):
        # put - сохранить данные на сервере
        try:
            payload = payload.strip()

            for row in payload.splitlines():
                key, value, timestamp = row.split()
                if key not in self.metric:
                    self.metric[key] = {}
                self.metric[key].update({int(timestamp): float(value)})
            return 'ok\n\n'

        except ValueError:
            return 'error\nwrong command\n\n'

    def get(self, get):
        # get — вернуть сохраненные данные с сервера
        get = get.strip().split(" ")
        result = ''
        try:
            for n in get:
                if n != '*' and self.metric.get(n) == None:
                    if len(get) == 1 and str(n).isdigit() == False:
                        return 'ok\n\n'
                    else:
                        return 'error\nwrong command\n\n'

                if n in self.metric:
                    for i, j in self.metric[n].items():
                        result += n + ' ' + str(j) + ' ' + str(i) + '\n'

                if n == '*':
                    for i, j in self.metric.items():
                        for e, y in j.items():
                            result += i + ' ' + str(y) + ' ' + str(e) + '\n'

            return 'ok\n' + result + '\n'

        except KeyboardInterrupt:
            return 'error\nwrong command\n\n'

# if __name__ == '__main__':
#     run_server('127.0.0.1', '8888')
