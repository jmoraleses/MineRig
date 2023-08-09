import json
import random

import Config
from StratumMessage import StratumMessage


class StratumClient:
    def __init__(self, socket, address, process):
        self.socket = socket
        self.address = address
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
            response_message = StratumMessage(response[1], response[2], response[0])
            response_json = response_message.to_json()

            print("Mensaje enviado: {}".format(response_json))

            # Enviar la respuesta
            self.send(response_json)

    def handle_stratum_message(self, message):
        if 'jsonrpc' in message:
            version = message['jsonrpc']
            if version == '2.0':
                return json.dumps(self.handle_stratum_v2(message))
        return json.dumps(self.handle_stratum_v1(message))

    def handle_stratum_v1(self, message):
        method = message['method']
        # params = message['params']

        if method == 'mining.subscribe':
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


    def handle_stratum_v2(self, message):
        method = message['method']

        if method == 'mining.subscribe':
            subscription_id_1 = random.randint(1, 100000)
            subscription_id_2 = random.randint(1, 100000)
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_subscribe_response_v2(1, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size)

        elif method == 'mining.notify':
            job_data = self.stratum_processing.create_job_stratum(protocol_version=2)
            response = self.create_mining_notify_response_v2(job_data)

        elif method == 'mining.set_difficulty':
            difficulty = Config.get_difficulty_target()
            response = self.create_mining_set_difficulty_response_v2(difficulty)

        elif method == 'mining.set_extranonce':
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_mining_set_extranonce_response_v2(extranonce1, extranonce2_size)

        else:
            response = {'error': 'Unknown method'}

        print(response)
        return response

    def create_subscribe_response_v2(self, id, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size):
        response = {
            "id": id,
            "result": {
                "subscription_id": subscription_id_1,
                "extranonce1": extranonce1,
                "extranonce2_size": extranonce2_size
            },
            "error": None
        }
        return response

    def create_mining_notify_response_v2(self, job_data):
        response = {
            'id': None,
            'method': 'mining.notify',
            'params': {
                'job_id': job_data['job_id'],
                'version': job_data['version'],
                'prevhash': job_data['prevhash'],
                'coinbase1': job_data['coinbase1'],
                'transactions': job_data['transactions'],
                'merkle_root': job_data['merkle_root'],
                'nbits': job_data['nbits'],
                'ntime': job_data['ntime'],
                'clean_jobs': job_data['clean_jobs']
            }
        }
        return response

    def create_mining_set_difficulty_response_v2(self, difficulty):
        response = {
            'id': None,
            'method': 'mining.set_difficulty',
            'params': {
                'difficulty': difficulty
            }
        }
        return response

    def create_mining_set_extranonce_response_v2(self, extranonce1, extranonce2_size):
        response = {
            'id': None,
            'method': 'mining.set_extranonce',
            'params': {
                'extranonce1': extranonce1,
                'extranonce2_size': extranonce2_size
            }
        }
        return response

