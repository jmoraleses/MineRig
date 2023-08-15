import asyncio
import json
import random
import time
import uuid

import shortuuid as shortuuid

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumMessage import StratumMessage
from StratumProcessing import StratumProcessing


class StratumClient:
    def __init__(self):
        self.reader = None
        self.writer = None
        self.process = None
        self.fetcher = None
        self.connected_miners = {}
        # self.loop = loop

    async def handle_miner(self, reader, writer):

        self.fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                            Config.get_bitcoin_password())

        self.reader = reader
        self.writer = writer

        addr = writer.get_extra_info('peername')
        print(f"Conexión desde {addr}")

        # Register the miner
        miner_id = str(addr)  # Or any other unique identifier
        self.connected_miners[miner_id] = writer
        ini = 0
        buffer = ""

        print("template:")
        self.template = await self.fetcher.get_block_template()
        self.process = StratumProcessing(Config.bitcoin, self.template)
        print("create job")
        job_data = self.process.create_job(1)
        while True:
            try:
                data = await reader.read(4096)
                if not data:
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    request = json.loads(line)

                    await self.run(writer, request)

                    fin = time.time()
                    transcurrido = fin - ini

                    if transcurrido > 60:
                        print("template:")
                        self.template = await self.fetcher.get_block_template()
                        self.process = StratumProcessing(Config.bitcoin, self.template)
                        print("create job")
                        job_data = self.process.create_job(1)
                        # print("¡template")
                        ini = time.time()

                    # Enviar difficulty
                    difficulty = Config.get_difficulty_target()
                    response = self.create_mining_set_difficulty_response(difficulty)
                    await self.send(response)
                    print("Mensaje enviado: {}".format(response))

                    # Enviar trabajo
                    response = self.create_mining_notify_response(job_data)
                    await self.send(response)
                    print("Mensaje enviado: Notify")
                    # print("Mensaje enviado: {}".format(response))

            except ConnectionResetError:
                print("La conexión se ha cerrado inesperadamente.")
            except Exception as e:
                print(f"Error: {e}")
                # Unregister the miner
                if miner_id in self.connected_miners:
                    del self.connected_miners[miner_id]

    async def run(self, writer, message):

        # if message:
        print("Mensaje recibido: {}".format(message))

        # Procesar los datos recibidos
        response = await self.handle_stratum_v1(message)

        if response:
            if type(response) is not bool:
                await self.send(response)


    async def send(self, response):
        self.writer.write(json.dumps(response).encode() + b'\n')


    def handle_stratum_message(self, message):
        response = None
        # if 'jsonrpc' in message:
        #     version = message['jsonrpc']
        #     if version == '2.0':
        #         response = self.handle_stratum_v2(message)
        #         pass
        # else:
        #     response = self.handle_stratum_v1(message)
        response = self.handle_stratum_v1(message)
        return response


    async def handle_stratum_v1(self, message):
        method = message['method']
        params = message['params']
        id = message['id']
        response = None

        if method == 'mining.subscribe':
            name = ""
            if params:
                name = params[0]

            # response = self.create_subscribe(message)
            response = self.create_subscribe_response(id, name)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.extranonce.subscribe':
            response = {
                "id": 3,
                "result": True,
                "error": None
            }

        elif method == 'mining.notify':
            job_data = self.process.create_job(protocol_version=1)
            response = self.create_mining_notify_response(job_data)
            # print("Mensaje enviado: {}".format(response))

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
            response = await self.handle_mining_submit(ntime, nonce)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.authorize':
            worker = params[0]
            password = params[1]
            response = self.handle_mining_authorize(worker, password)
            print("Mensaje enviado: {}".format(response))

        return response

    def create_subscribe(self, message):
        response = message
        return response

    def create_subscribe_response(self, id, name):
        print("subscribe:")
        # name = params
        notification_id = str(uuid.uuid4()).replace("-", "")
        # # block_target = self.process.block_bits2target().hex()
        nonce = Config.get_nonce()
        extranonce1 = Config.get_extranonce1()  # Este valor es fijo
        extranonce2 = Config.get_extranonce2()
        # difficulty = self.process.calculate_difficulty()

        response = {
            'id': id,
            'result': [
                [
                    'mining.set_difficulty',
                        notification_id
                ],
                extranonce1,
                extranonce2
            ],
            'error': None
        }

        return response

    def create_mining_notify_response(self, job_data):
        print("set notify:")
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
        print("set difficulty:")
        response = {
            "id": None,
            "method": "mining.set_difficulty",
            "params": [difficulty]
        }
        return response

    def create_mining_set_extranonce_response(self, extranonce1, extranonce2_size):
        print("set extranonce:")
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
        print("set transactions:")
        transactions = self.process.select_random_transactions()  # Obtener las transacciones desde la base de datos
        response = {
            'result': transactions,
            'error': None,
            'id': None
        }
        return response

    async def handle_mining_submit(self, ntime, nonce):
        print("put submit:")
        # Verificar si el resultado es válido
        block_submission = self.process.block_validate(ntime, nonce)

        # is_sent_rpc = await BlockTemplateFetcher.submitblock(block_submission)
        is_sent_rpc = await self.fetcher.submitblock(block_submission)

        if is_sent_rpc is True:
            response = {
                'id': None,
                'result': True,
                'error': None
            }
        else:
            response = {
                'id': None,
                'result': False,
                'error': 'Invalid result'
            }

        return response

    def handle_mining_authorize(self, worker, password):
        # Verificar las credenciales del trabajador
        # if self.verify_worker_credentials(worker, password) is True:
        response = {
            "id": 2,
            "result": True,
            "error": None
        }
        # self.writer.write(json.dumps(response).encode('utf-8') + b'\n')
        # else:
        #     response = {
        #         'result': False,
        #         'error': 'Invalid credentials',
        #         'id': 2
        #     }
        # print(response)
        return response

    def verify_worker_credentials(self, worker, password):
        if worker == Config.get_worker() and password == Config.get_worker_password():
            return True
        return False

    #
    # async def handle_stratum_v2(self, message):
    #     method = message['method']
    #     params = message['params']
    #     response = None
    #
    #     if method == 'mining.subscribe':
    #         subscription_id_1 = random.randint(1, 100000)
    #         subscription_id_2 = random.randint(1, 100000)
    #         extranonce2 = Config.get_extranonce2()
    #         extranonce2_size = Config.get_difficulty_target()
    #         response = self.create_subscribe_response_v2(1, subscription_id_1, subscription_id_2, extranonce2, extranonce2_size)
    #
    #     elif method == 'mining.notify':
    #         job_data = self.process.create_job(protocol_version=2)
    #         response = self.create_mining_notify_response_v2(job_data)
    #
    #     elif method == 'mining.set_difficulty':
    #         difficulty = Config.get_difficulty_target()
    #         response = self.create_mining_set_difficulty_response_v2(difficulty)
    #
    #     elif method == 'mining.set_extranonce':
    #         extranonce1 = Config.get_extranonce1()
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
    #         response = await self.handle_mining_submit(ntime, nonce)
    #
    #     elif method == 'mining.authorize':
    #         worker = params[0]
    #         password = params[1]
    #         response = self.handle_mining_authorize(worker, password)
    #
    #     return response
    #
    # def create_subscribe_response_v2(self, id, subscription_id_1, subscription_id_2, extranonce2, extranonce2_size):
    #     response = {
    #         'id': id,
    #         'result': {
    #             'subscription_id': subscription_id_1,
    #             'extranonce1': extranonce2,
    #             'extranonce2_size': extranonce2_size
    #         },
    #         'error': None
    #     }
    #
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
    #     transactions = self.process.select_random_transactions()  # Obtener las transacciones desde la base de datos
    #     response = {
    #         'id': None,
    #         'method': 'mining.get_transactions',
    #         'params': {
    #             'transactions': transactions
    #         }
    #     }
    #     return response
