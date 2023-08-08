import socket
import json
import time

HOST = 'localhost'
PORT = 3333

def receive_json(client_sock):
    buffer = ""
    while True:
        chunk = client_sock.recv(4096).decode('utf-8')
        if not chunk:
            break
        buffer += chunk
        try:
            message = json.loads(buffer)
            buffer = ""
            return message
        except json.JSONDecodeError:
            continue
    return None

def subscribe(client_sock):
    msg = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
    }
    client_sock.sendall(json.dumps(msg).encode('utf-8') + b'\n')
    response = receive_json(client_sock)
    print("Respuesta de suscripción:", response)

def authorize(client_sock, username, password):
    msg = {
        "id": 2,
        "method": "mining.authorize",
        "params": [username, password]
    }
    client_sock.sendall(json.dumps(msg).encode('utf-8') + b'\n')
    response = receive_json(client_sock)
    print("Respuesta de autorización:", response)

def submit_solution(client_sock, username, job_id, extranonce2, ntime, nonce):
    msg = {
        "id": 4,
        "method": "mining.submit",
        "params": [
            username,
            job_id,
            extranonce2,
            ntime,
            nonce
        ]
    }
    client_sock.sendall(json.dumps(msg).encode('utf-8') + b'\n')
    response = receive_json(client_sock)
    print("Respuesta de presentación:", response)

def simulate_mining(client_sock, username):
    while True:
        work_notification = receive_json(client_sock)
        print("Notificación de trabajo recibida:", work_notification)

        # Simulando la búsqueda de una solución (en la realidad, esto implicaría una gran cantidad de cálculo)
        # time.sleep(1)

        # Simulando la presentación de una solución
        job_id = work_notification['params']
        extranonce2 = "05f812a5"
        ntime = 1691342182
        nonce = 4501521
        submit_solution(client_sock, username, job_id, extranonce2, ntime, nonce)

def connect_to_stratum_server(host, port, username, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((host, port))
        subscribe(client_sock)
        authorize(client_sock, username, password)
        simulate_mining(client_sock, username)

if __name__ == '__main__':
    print("Iniciando rig de minería...")
    connect_to_stratum_server(HOST, PORT, "jmorales", "x")