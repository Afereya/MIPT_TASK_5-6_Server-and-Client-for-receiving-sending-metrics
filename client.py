import socket
import time


class Client:
    """
    Необходимо реализовать класс Client, в котором будет инкапсулировано соединение с сервером,
    клиентский сокет и методы для получения и отправки метрик на сервер.
    В конструктор класса Client должна передаваться адресная пара хост и порт,
    а также необязательный аргумент timeout (timeout=None по умолчанию).
    У класса Client должно быть 2 метода: put и get, соответствующих протоколу выше.
    """
    def __init__(self, host, port, timeout=None):
        self.socket = socket.create_connection((host, port), timeout)

    def get(self, key):
        """
        Формат команды get для получения метрик — это строка вида:

        get <key>\n

        В качестве ключа можно указывать символ *, для этого символа будут возвращены все доступные метрики.
        В данном задании мы никак не ограничиваем количество метрик, которые должен вернуть сервер – сервер должен возвращать все метрики, удовлетворяющие ключу.

        Успешный ответ от сервера:

        ok\npalm.cpu 10.5 1501864247\neardrum.cpu 15.3 1501864259\n\n

        Если ни одна метрика не удовлетворяет условиям поиска, то вернется ответ:

        ok\n\n

        Обратите внимание, что каждая успешная операция начинается с "ok", а за ответом сервера всегда указано два символа \n.

        Клиент получает данные в текстовом виде, метод get должен возвращать словарь с полученными ключами с
        сервера. Значением ключа в словаре является список кортежей [(timestamp, metric_value), ...],
        отсортированный по timestamp от меньшего к большему. Значение timestamp должно быть преобразовано к
        целому числу int. Значение метрики metric_value нужно преобразовать к числу с плавающей точкой float.

        Метод get принимает первым аргументом имя метрики, значения которой мы хотим выгрузить.
        Также вместо имени метрики можно использовать символ *, о котором говорилось в описании протокола.

        Метод get возвращает словарь с метриками (смотрите ниже пример) в случае успешного получения ответа от
        сервера и выбрасывает исключение ClientError в случае неуспешного.

        Пример возвращаемого значения при успешном вызове client.get("palm.cpu"):

        {
          'palm.cpu': [
            (1150864247, 0.5),
            (1150864248, 0.5)
          ]
        }

        Пример возвращаемого значения при успешном вызове client.get("*"):

        {
          'palm.cpu': [
            (1150864247, 0.5),
            (1150864248, 0.5)
          ],
          'eardrum.cpu': [
            (1150864250, 3.0),
            (1150864251, 4.0)
          ],
          'eardrum.memory': [
            (1503320872, 4200000.0)
          ]
        }

        Если в ответ на get-запрос сервер вернул положительный ответ ok\n\n,
        но без данных (то есть данных по запрашиваемому ключу нет), то метод get клиента должен вернуть пустой словарь:

        >>> client = Client("127.0.0.1", 8888)
        >>> client.get("non_existing_key")
        {}

        :param key: ключ или *
        :return:
        """
        try:
            self.socket.sendall(f"get {key}\n".encode())
            answer = b""
            while not answer.count(b"\n\n"):
                answer += self.socket.recv(1000)
            response = answer.decode()
            lst = [s for s in response.split('\n') if s != 'ok' and s != '']
            d = {}
            for item in lst:
                fields = item.split(' ')
                if fields[0] not in d:
                    d[fields[0]] = []
                d[fields[0]].append((int(fields[2]), float(fields[1])))
            # print(d)
        except:
            raise ClientError()
        return d

    def put(self, metric, value, timestamp=None):
        """
        Метод put принимает первым аргументом название метрики, вторым численное значение, третьим - необязательный
        именованный аргумент timestamp.
        Если пользователь вызвал метод put без аргумента timestamp, то клиент автоматически должен подставить
        текущее время в команду put - str(int(time.time()))

        Метод put не возвращает ничего в случае успешной отправки и выбрасывает исключение ClientError
        в случае неуспешной.
        :param metric: название метрики
        :param value: численное значение
        :param timestamp:
        :return:
        """
        timestamp = timestamp or int(time.time())
        try:
            self.socket.sendall(f"put {metric} {value} {timestamp}\n".encode())
            answer = self.socket.recv(256)
        except:
            raise ClientError()


class ClientError(Exception):
    pass

# client = Client("127.0.0.1", 8181)
#
# client.put("palm.cpu", 0.5, timestamp=1150864247)
# client.put("palm.cpu", 2.0, timestamp=1150864248)
# client.put("palm.cpu", 0.5, timestamp=1150864248)
#
# client.put("eardrum.cpu", 3, timestamp=1150864250)
# client.put("eardrum.cpu", 4, timestamp=1150864251)
# client.put("eardrum.memory", 4200000)
#
# print(client.get("*"))