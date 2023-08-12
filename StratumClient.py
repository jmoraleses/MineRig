import asyncio
import json
import random
import uuid

import shortuuid as shortuuid

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumMessage import StratumMessage
from StratumProcessing import StratumProcessing


class StratumClient:
    def __init__(self, socket, process):
        self.socket = socket
        self.process = process
        # self.loop = loop

    async def run(self):

        data = self.receive()

        if data:

            message = data

            print("Mensaje recibido: {}".format(message))


            # Procesar los datos recibidos
            response = self.handle_stratum_v1(message)

            response = json.dumps(response)

            # Enviar respuesta al cliente
            await self.send(response)



    def receive(self):
        buffer = ""
        while True:
            chunk = None
            try:
                chunk = self.socket.recv(1024).decode()
            except ConnectionAbortedError as e:
                # Manejar la excepción aquí
                print("La conexión ha sido anulada por el software en el equipo host.")

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

    async def send(self, data):
        self.socket.sendall(data.encode())

    def close(self):
        self.socket.close()



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
            name = ""
            if params:
                name = params[0]
            response = self.create_subscribe_response(id, name)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.notify':
            job_data = self.process.create_job_stratum(protocol_version=1)
            response = self.create_mining_notify_response(job_data)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.set_difficulty':
            difficulty = Config.get_difficulty_target()
            response = self.create_mining_set_difficulty_response(difficulty)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.set_extranonce':
            extranonce1 = Config.get_extranonce2()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_mining_set_extranonce_response(extranonce1, extranonce2_size)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.get_transactions':
            response = self.handle_mining_get_transactions()
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.submit':
            ntime = params[3]
            nonce = params[4]
            response = self.handle_mining_submit(id, ntime, nonce)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.authorize':
            worker = params[0]
            password = params[1]
            response = self.handle_mining_authorize(id, worker, password)
            # response_json = json.dumps(response)
            print("Mensaje enviado: {}".format(response))
            # self.socket.sendall(response_json.encode())
            # job_data = self.process.create_job_stratum(protocol_version=1)
            # response = self.create_mining_notify_response(job_data)
            # # response_json = json.dumps(response)
            # print("Mensaje enviado: {}".format(response))
        return response

    def create_subscribe_response(self, id, name):
        # name = params
        notification_id = str(uuid.uuid4()).replace("-", "")
        # # block_target = self.process.block_bits2target().hex()
        nonce = Config.get_nonce()
        extranonce1 = Config.get_extranonce1()  # Este valor es fijo
        # difficulty = self.process.calculate_difficulty()
        # response = {
        #     "id": id,
        #     "result": [
        #         name,
        #         notification_id
        #     ],
        #     "error": None
        # }


        response = {
            'result': [
                [
                    [
                        'mining.set_difficulty',
                        extranonce1
                    ],
                    [
                        'mining.notify',
                        extranonce1
                    ]
                ],
                nonce,
                4
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

    def handle_mining_get_transactions(self):
        transactions = self.process.select_random_transactions()  # Obtener las transacciones desde la base de datos
        response = {
            'result': transactions,
            'error': None,
            'id': None
        }
        return response

    def handle_mining_submit(self, id, ntime, nonce):

        # Verificar si el resultado es válido
        block_submission = self.process.block_validate(ntime, nonce)

        if block_submission is not False:
            is_sent_rpc = BlockTemplateFetcher.submitblock(block_submission)

            response = {
                'id': id,
                'result': True,
                'error': None

            }
        else:
            response = {
                'id': id,
                'result': False,
                'error': 'Invalid result'
            }

        return response

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


    def handle_stratum_v2(self, message):
        method = message['method']
        params = message['params']
        response = None

        if method == 'mining.subscribe':
            subscription_id_1 = random.randint(1, 100000)
            subscription_id_2 = random.randint(1, 100000)
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_subscribe_response_v2(1, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size)

        elif method == 'mining.notify':
            job_data = self.process.create_job_stratum(protocol_version=2)
            response = self.create_mining_notify_response_v2(job_data)

        elif method == 'mining.set_difficulty':
            difficulty = Config.get_difficulty_target()
            response = self.create_mining_set_difficulty_response_v2(difficulty)

        elif method == 'mining.set_extranonce':
            extranonce1 = Config.get_extranonce()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_mining_set_extranonce_response_v2(extranonce1, extranonce2_size)

        elif method == 'mining.get_transactions':
            response = self.handle_mining_get_transactions_v2()

        elif method == 'mining.submit':
            worker = params[0]
            job_id = params[1]
            extranonce2 = params[2]
            ntime = params[3]
            nonce = params[4]
            response = self.handle_mining_submit(worker, job_id, extranonce2, ntime, nonce)

        elif method == 'mining.authorize':
            worker = params[0]
            password = params[1]
            response = self.handle_mining_authorize(worker, password)

        return response

    def create_subscribe_response_v2(self, id, subscription_id_1, subscription_id_2, extranonce1, extranonce2_size):
        response = {
            'id': id,
            'result': {
                'subscription_id': subscription_id_1,
                'extranonce1': extranonce1,
                'extranonce2_size': extranonce2_size
            },
            'error': None
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

    def handle_mining_get_transactions_v2(self):
        transactions = self.process.select_random_transactions()  # Obtener las transacciones desde la base de datos
        response = {
            'id': None,
            'method': 'mining.get_transactions',
            'params': {
                'transactions': transactions
            }
        }
        return response
