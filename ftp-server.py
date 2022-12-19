import socket  # библиотека для обмена информацией между процессами
import sys  # библиотека для получения данных о системе
import threading  # билиотека для работы с потоками
import os  # библиотека для работы с системой

dirname = os.path.join(os.getcwd(), 'docs')


def process(req):
    req = req.split()       # разделение по пробелу
    if req[0] == 'pwd':     # или запрос - 'pwd' - показывает название рабочей директории
        return dirname      # возвращаем имя директории
    elif req[0] == 'ls':    # если запрос - 'ls' - показывает содержимое текущей директории
        return '; '.join(os.listdir(dirname))   # возвращаем содержимое через ';'
    elif req[0] == 'mkdir':     # если запрос - 'mkrir' - создание директории
        if not os.path.exists(os.path.join(dirname, req[1])):   # если такой директории не существует
            os.makedirs(os.path.join(dirname, req[1]))      # создаем директорию
            return os.path.join(dirname, req[1])        # возвращаем путь к директории
        else:
            return "aleady exists"      # иначе возвращаем, что директория уже существует
    else:
        return 'bad request'        # иначе возвращем 'bad request'


def run_server(port=53210):     # сервер на порту 53210
    serv_sock = create_serv_sock(port)  # вызов функции create_serv_sock
    cid = 0
    while True:
        client_sock = accept_client_conn(serv_sock, cid)    # вызов функции accept_client_conn
        t = threading.Thread(target=serve_client,
                             args=(serv_sock, client_sock, cid))    # разбиваем на потоки
        t.start()   # стартуем поток
        cid += 1


def serve_client(serv_sock, client_sock, cid):
    while True:
        request = read_request(client_sock)     # получаем запрос
        if request is None:     # если нет запроса
            print(f'Client #{cid} unexpectedly disconnected')
            break
        else:
            if 'exit' in request.decode('utf-8'):       # если запрос - exit
                write_response_close(client_sock, 'exit'.encode('utf-8'), cid)      # даем ответ клиенту
                break
            if 'stop' in request.decode('utf-8'):      # если запрос - stop
                write_response_closes(serv_sock, client_sock, 'cstop'.encode('utf-8'), cid)     # даем ответ клиенту
                break
            response = handle_request(request.decode('utf-8'))      # декодируем запрос
            write_response(client_sock, response.encode('utf-8'))   # даем ответ


def create_serv_sock(serv_port):
    serv_sock = socket.socket(socket.AF_INET,
                              socket.SOCK_STREAM,
                              proto=0)      # создаем сокет
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # управляем параметрами сокета

    serv_sock.bind(('', serv_port))     # связываем сервер с портом
    serv_sock.listen()      # слушаем сокет
    return serv_sock


def accept_client_conn(serv_sock, cid):
    client_sock, client_addr = serv_sock.accept()       # извлекаем запрос на подключение
    print(f'Client #{cid} connected '
          f'{client_addr[0]}:{client_addr[1]}')     # выводим информацию о подключении
    return client_sock


def read_request(client_sock):
    try:
        request = client_sock.recv(1024)        # получаем ответ
        if not request:  # Клиент преждевременно отключился.
            return None
        return request

    except ConnectionResetError:  # Соединение было неожиданно разорвано.
        return None
    except Exception:       # в случае другой ошибки
        raise


def handle_request(request):
    return process(request)


def write_response(client_sock, response):
    client_sock.sendall(response)       # посылаем ответ


def write_response_close(client_sock, response, cid):
    client_sock.sendall(response)       # посылаем ответ
    client_sock.close()     # закрываем соединение
    print(f'Client #{cid} has been served')


def write_response_closes(serv_sock, client_sock, response, cid):
    client_sock.sendall(response)       # посылаем ответ
    client_sock.close()     # закрываем соединение
    serv_sock.close()       # закрываем сокет
    print(f'Client #{cid} has been stoped server')
    os._exit(0)     # выходим из процесса с определенным статусом


if __name__ == '__main__':      # конструция для старта программы
    try:
        run_server(port=int(sys.argv[1]))       # запускаем сервер
    except Exception:       # в случае ошибки
        os._exit(0)     # выходим из процесса с определенным статусом#
