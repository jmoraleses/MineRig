import unittest
import socket
import json

HOST = '127.0.0.1' #'pool3.ddns.net'
PORT = 3333

class StratumCommunicationTest(unittest.TestCase):
    def setUp(self):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((HOST, PORT))

    def tearDown(self):
        self.client_sock.close()

    def send_request(self, method, params):
        request = {
            "id": 1,
            "method": method,
            "params": params
        }
        self.client_sock.sendall(json.dumps(request).encode('utf-8') + b'\n')
        response = self.receive_json()
        return response

    def receive_json(self):
        buffer = ""
        while True:
            chunk = None
            try:
                chunk = self.client_sock.recv(1024).decode('utf-8')
            except ConnectionAbortedError as e:
                # Manejar la excepción aquí
                raise ConnectionError("La conexión ha sido anulada por el software en el equipo host.")

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

    def test_subscribe(self):
        response = self.send_request("mining.subscribe", [])
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("id", response)
        self.assertEqual(response["id"], 1)

    def test_authorize(self):
        response = self.send_request("mining.authorize", ["username", "password"])
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("id", response)
        self.assertEqual(response["id"], 1)

    def test_submit_solution(self):
        response = self.send_request("mining.submit", ["username", "job_id", "extranonce2", 1691342182, 152452])
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("id", response)
        self.assertEqual(response["id"], 1)

if __name__ == '__main__':
    unittest.main()