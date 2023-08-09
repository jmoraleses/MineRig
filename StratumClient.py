import json
import random

import Config
from StratumMessage import StratumMessage
from StratumSession import StratumSession


class StratumClient:
    def __init__(self, socket, address, process):
        self.socket = socket
        self.address = address
        self.session = StratumSession(self)
        self.stratum_processing = process

    def send(self, message):
        self.socket.sendall(message.encode())

    def receive(self):
        data = self.socket.recv(1024).decode()
        return json.loads(data)

    def close(self):
        self.socket.close()

    def run(self):
        while True:
            message = self.receive()
            print("Mensaje recibido: {}".format(message))

            # Gestionamos la salida dado el mensaje entrante
            response = self.handle_stratum_message(message)

            # Convertir la respuesta a formato JSON utilizando StratumMessage
            response_message = StratumMessage(response['method'], response['params'], response['id'])
            response_json = response_message.to_json()

            print(response_json)

            # Enviar la respuesta
            self.send(response_json)


    def handle_stratum_message(self, message):
        version = message.get('version')

        if version == 'Stratum/1.0.0' or version is None:
            return self.handle_stratum_v1(message)
        elif version == 'Stratum/2.0.0':
            # data = self.handle_stratum_v2(message)
            pass
        else:
            response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32600,
                    'message': 'Versión no soportada'
                },
                'id': None
            }
            return response

    def handle_stratum_v1(self, message):
        method = message['method']
        params = message['params']


        if method == 'mining.subscribe':
            # subscription_id_1, subscription_id_2 = self.extract_subscription_ids(message)
            subscription_id_1 = random.randint(1, 100000)
            subscription_id_2 = random.randint(1, 100000)
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_subscribe_response(1, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size)

        elif method == 'mining.notify':
            job_data = self.stratum_processing.create_job_stratum(protocol_version=1)
            response = self.create_mining_notify_response(job_data)

        elif method == 'mining.set_difficulty':
            difficulty = Config.get_difficulty_target()
            response = self.create_mining_set_difficulty_response(difficulty)

        elif method == 'mining.set_extranonce':
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_mining_set_extranonce_response(extranonce1, extranonce2_size)

        else:
            response = {'error': 'Unknown method'}

        print(response)
        return response


    # def extract_subscription_ids(self, message):
    #     subscription_id_1 = message['params'][0][0][1]
    #     subscription_id_2 = message['params'][0][1][1]
    #     return subscription_id_1, subscription_id_2

    def create_subscribe_response(self, id, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size):
        response = {
            "id": id,
            "result": [
                [
                    ["mining.set_difficulty", subscription_id_1],
                    ["mining.notify", subscription_id_2]
                ],
                extranonce1,
                extranonce2_size
            ],
            "error": None
        }
        return response

    def create_mining_notify_response(self, job_data):
        response = {
            'id': None,
            'method': 'mining.notify',
            'params': [
                job_data['job_id'],
                job_data['version'],
                job_data['prevhash'],
                job_data['coinbase1'],
                job_data['transactions'],
                job_data['merkle_root'],
                job_data['nbits'],
                job_data['ntime'],
                job_data['clean_jobs']
            ]
        }
        return response

    def create_mining_set_difficulty_response(self, difficulty):
        response = {
            'id': None,
            'result': True,
            'error': None,
            'params': [
                difficulty
            ]
        }
        return response

    def create_mining_set_extranonce_response(self, extranonce1, extranonce2_size):
        response = {
            'id': None,
            'method': 'mining.set_extranonce',
            'params': [
                extranonce1,
                extranonce2_size
            ]
        }
        return response