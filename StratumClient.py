import json
import random
import socket
import uuid

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumMessage import StratumMessage


class StratumClient:
    def __init__(self, socket, address, process):
        self.socket = socket
        self.address = address
        self.stratum_processing = process

    def send(self, message):
        self.socket.sendall(message.encode())

    def receive(self):
        buffer = ""
        while True:
            chunk = self.socket.recv(1024).decode('utf-8')
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

    def close(self):
        self.socket.close()

    async def run(self):
        while True:

                message = self.receive()

                if message is not None:
                    print("Mensaje recibido: {}".format(message))

                    # Gestionamos la salida dado el mensaje entrante
                    response = self.handle_stratum_message(message)

                    # Convertir la respuesta a formato JSON utilizando StratumMessage
                    response_json = json.dumps(response)
                    # response_message = StratumMessage(response)
                    # response_json = response_message.to_json()

                    print("Mensaje enviado: {}".format(response_json))

                    # Enviar la respuesta
                    self.send(response_json)
                    print()

                else:
                    break

    def handle_stratum_message(self, message):
        response = None
        if 'jsonrpc' in message:
            version = message['jsonrpc']
            if version == '2.0':
                # response = self.handle_stratum_v2(message)
                pass
        else:
            response = self.handle_stratum_v1(message)
        return response

    def handle_stratum_v1(self, message):
        method = message['method']
        params = message['params']
        id = message['id']
        response = None

        if method == 'mining.subscribe':
            # subscription_id_1 = random.randint(1, 100000)
            # subscription_id_2 = random.randint(1, 100000)
            # extranonce1 = Config.get_extranonce()
            # extranonce2_size = Config.get_difficulty_target()
            # response = self.create_subscribe_response(1, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size)
            response = self.create_subscribe_response(id)

            # response_json = json.dumps(response)
            # self.send(response_json)
            # response = self.send_authorization()

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

        elif method == 'mining.get_transactions':
            response = self.handle_mining_get_transactions()

        elif method == 'mining.submit':
            worker = params[0]
            job_id = params[1]
            extranonce2 = params[2]
            ntime = params[3]
            nonce = params[4]

            response = self.handle_mining_submit(id, worker, job_id, extranonce2, ntime, nonce)

        elif method == 'mining.authorize':
            worker = params[0]
            password = params[1]
            response = self.handle_mining_authorize(id, worker, password)

        return response


    def create_subscribe_response(self, id):

        notification_id = str(uuid.uuid4()).replace("-", "")
        nonce = Config.get_nonce()
        block_target = self.stratum_processing.block_bits2target().hex()
        extranonce1 = Config.get_extranonce()
        difficulty = Config.get_difficulty_target()

        # {“result”:[[[“mining.set_difficulty”, “731ec5e0649606ff”], [“mining.notify”, “731ec5e0649606ff”]], “e9695791”, 4], “id”:1,“error”:null}

        response = {
            'result': [
                [
                    [
                        'mining.set_difficulty',
                        notification_id
                    ],
                    [
                        'mining.notify',
                        notification_id
                    ]
                ],
                nonce,
                difficulty
            ],
            'id': id,
            'error': None
        }

        return response

    def create_mining_notify_response(self, job_data):
        response = {
            'id': None,
            'method': 'mining.notify',
            'params': [
                job_data['job_id'],
                job_data['prevhash'],
                job_data['coinbase1'],
                job_data['transactions'],
                job_data['merkle_root'],
                job_data['version'],
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

    def handle_mining_get_transactions(self):
        transactions = self.stratum_processing.select_random_transactions()  # Obtener las transacciones desde la base de datos
        response = {
            'result': transactions,
            'error': None,
            'id': None
        }
        return response

    # {“id”: 2, “result”: true, “error”: null}
    def handle_mining_submit(self, id, worker, job_id, extranonce2, ntime, nonce):
        is_sent = False

        # Verificar si el resultado es válido
        block_submission = self.stratum_processing.block_validate(ntime, nonce)
        if block_submission is not False:
            is_sent = BlockTemplateFetcher.submitblock(block_submission)

        if is_sent:
            response = {
                'id': id,
                'result': True,
                'error': None

            }
        else:
            response = {
                'result': False,
                'error': 'Invalid result',
                'id': id
            }

        return response

    # {“id”: 2, “result”: true, “error”: null}
    def handle_mining_authorize(self, id, worker, password):
        # Verificar las credenciales del trabajador
        if self.verify_worker_credentials(worker, password):
            response = {
                "id": id,
                "result": True,
                "error": None
            }
        else:
            response = {
                'result': False,
                'error': 'Invalid credentials',
                'id': id
            }

        return response

    def verify_worker_credentials(self, worker, password):
        if worker == Config.get_worker() and password == Config.get_worker_password():
            return True
        return False

    #
    # def handle_stratum_v2(self, message):
    #     method = message['method']
    #     params = message['params']
    #     response = None
    #
    #     if method == 'mining.subscribe':
    #         subscription_id_1 = random.randint(1, 100000)
    #         subscription_id_2 = random.randint(1, 100000)
    #         extranonce1 = Config.get_extranonce()
    #         extranonce2_size = Config.get_difficulty_target()
    #         response = self.create_subscribe_response_v2(1, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size)
    #
    #     elif method == 'mining.notify':
    #         job_data = self.stratum_processing.create_job_stratum(protocol_version=2)
    #         response = self.create_mining_notify_response_v2(job_data)
    #
    #     elif method == 'mining.set_difficulty':
    #         difficulty = Config.get_difficulty_target()
    #         response = self.create_mining_set_difficulty_response_v2(difficulty)
    #
    #     elif method == 'mining.set_extranonce':
    #         extranonce1 = Config.get_extranonce()
    #         extranonce2_size = Config.get_difficulty_target()
    #         response = self.create_mining_set_extranonce_response_v2(extranonce1, extranonce2_size)
    #
    #     elif method == 'mining.get_transactions':
    #         response = self.handle_mining_get_transactions_v2()
    #
    #     elif method == 'mining.submit':
    #         worker = params[0]
    #         job_id = params[1]
    #         extranonce2 = params[2]
    #         ntime = params[3]
    #         nonce = params[4]
    #         response = self.handle_mining_submit(worker, job_id, extranonce2, ntime, nonce)
    #
    #     elif method == 'mining.authorize':
    #         worker = params[0]
    #         password = params[1]
    #         response = self.handle_mining_authorize(worker, password)
    #
    #     return response
    #
    # def create_subscribe_response_v2(self, id, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size):
    #     response = {
    #         'id': id,
    #         'result': {
    #             'subscription_id': subscription_id_1,
    #             'extranonce1': extranonce1,
    #             'extranonce2_size': extranonce2_size
    #         },
    #         'error': None
    #     }
    #     return response
    #
    # def create_mining_notify_response_v2(self, job_data):
    #     response = {
    #         'id': None,
    #         'method': 'mining.notify',
    #         'params': {
    #             'job_id': job_data['job_id'],
    #             'version': job_data['version'],
    #             'prevhash': job_data['prevhash'],
    #             'coinbase1': job_data['coinbase1'],
    #             'transactions': job_data['transactions'],
    #             'merkle_root': job_data['merkle_root'],
    #             'nbits': job_data['nbits'],
    #             'ntime': job_data['ntime'],
    #             'clean_jobs': job_data['clean_jobs']
    #         }
    #     }
    #     return response
    #
    # def create_mining_set_difficulty_response_v2(self, difficulty):
    #     response = {
    #         'id': None,
    #         'method': 'mining.set_difficulty',
    #         'params': {
    #             'difficulty': difficulty
    #         }
    #     }
    #     return response
    #
    # def create_mining_set_extranonce_response_v2(self, extranonce1, extranonce2_size):
    #     response = {
    #         'id': None,
    #         'method': 'mining.set_extranonce',
    #         'params': {
    #             'extranonce1': extranonce1,
    #             'extranonce2_size': extranonce2_size
    #         }
    #     }
    #     return response
    #
    # def handle_mining_get_transactions_v2(self):
    #     transactions = self.stratum_processing.select_random_transactions()  # Obtener las transacciones desde la base de datos
    #     response = {
    #         'id': None,
    #         'method': 'mining.get_transactions',
    #         'params': {
    #             'transactions': transactions
    #         }
    #     }
    #     return response
