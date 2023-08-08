import socket
import json
import time

def connect(host, port):
    # Crear socket y conectarse al servidor Stratum
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Enviar mensaje de inicio de sesión
    message = {
        'jsonrpc': '2.0',
        'method': 'login',
        'params': {
            'session_id': 'my_session_id',
            'user_id': 'my_user_id',
            'auth_token': 'my_auth_token'
        },
        'id': 1
    }
    client_socket.sendall(json.dumps(message).encode())

    # Recibir respuesta del servidor Stratum
    data = client_socket.recv(1024).decode()
    response = json.loads(data)
    print(response)

    # Esperar un segundo
    time.sleep(1)

    # Enviar mensaje de minería
    message = {
        'jsonrpc': '2.0',
        'method': 'mining.submit',
        'params': {
            'session_id': 'my_session_id',
            'user_id': 'my_user_id',
            'auth_token': 'my_auth_token',
            'job_id': 'my_job_id',
            'nonce': 'my_nonce',
            'result': 'my_result'
        },
        'id': 2
    }
    client_socket.sendall(json.dumps(message).encode())

    # Recibir respuesta del servidor Stratum
    data = client_socket.recv(1024).decode()
    response = json.loads(data)
    print(response)

    # Cerrar conexión
    client_socket.close()

if __name__ == '__main__':
    connect('localhost', 3333)