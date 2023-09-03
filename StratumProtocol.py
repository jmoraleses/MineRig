import asyncio
import json
import time
import uuid

import Config


class StratumProtocol(asyncio.Protocol):

    def __init__(self, process, coinbase_message, transactions, merkleroot, job_data):
        self.process = process
        self.coinbase_message = coinbase_message
        self.transactions = transactions
        self.merkleroot = merkleroot
        self.job_data = job_data
        self.extranonce2 = None
        self.ntime = None
        self.nonce = None
        self.is_sent_rpc = False

    async def handle_stratum_v1(self, message):

        method = message['method']
        params = message['params']
        id = message['id']
        response = ""

        if method == 'mining.extranonce.subscribe':
            response = ('{{"id": {id}, "result": true, "error": null}}\n'.format(id=id))
            print("Mensaje enviado: {}".format(response))

        if method == 'mining.subscribe':
            # name = params[0]
            response = self.create_subscribe_response(id)  # name
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.notify':
            # job_data = self.process.create_job(protocol_version=2)
            response = self.create_mining_notify_response(id)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.set_difficulty':
            difficulty = Config.get_difficulty_target()
            # difficulty = self.process.calculate_difficulty() ###
            response = self.create_mining_set_difficulty_response(id, difficulty)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.set_extranonce':
            extranonce1 = Config.get_extranonce2()
            extranonce2_size = Config.get_difficulty_target()
            response = self.create_mining_set_extranonce_response(id, extranonce1, extranonce2_size)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.get_transactions':
            response = self.handle_mining_get_transactions()
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.submit':
            self.extranonce2 = params[2]
            self.ntime = params[3]
            self.nonce = params[4]
            response = await self.handle_mining_submit(id, self.extranonce2, self.ntime, self.nonce)
            print("Mensaje enviado: {}".format(response))
            # return [self.extranonce2, self.ntime, self.nonce]

        elif method == 'mining.multi_version':
            response = self.handle_mining_multi_version(id)
            print("Mensaje enviado: {}".format(response))

        elif method == 'mining.authorize':
            worker = params[0]
            password = params[1]

            response = self.handle_mining_authorize(id, worker, password)
            print("Mensaje enviado: {}".format(response))
            self.send(response)

            difficulty = Config.get_difficulty_target()
            response = self.create_mining_set_difficulty_response(id, difficulty)
            print("Mensaje enviado: {}".format(response))
            self.send(response)

            # enviar mining.notify
            response = self.create_mining_notify_response(id)
            print("Mensaje enviado: {}".format(response))
            self.send(response)

        return response

    def create_subscribe_response(self, id):  # name
        notification_id = str(uuid.uuid4()).replace("-", "")
        # # block_target = self.process.block_bits2target().hex()
        # nonce = Config.get_nonce()
        extranonce1 = Config.get_extranonce1()  # Este valor es fijo
        extranonce2 = Config.get_extranonce2()
        difficulty = Config.get_extranonce2_size()  # tamaño de extranonce
        response = (
            '{{ "id": {id}, "result": [ [ ["mining.set_difficulty", "{notification_id}"], ["mining.notify", "{extranonce1}"] ], "{extranonce2}", {difficulty}], "error": null}}\n'.format(
                id=id, notification_id=notification_id, extranonce1=extranonce1, extranonce2=extranonce2,
                difficulty=difficulty))
        # response = ('{{"id": {id}, "result": [ [ ["mining.set_difficulty", "b4b6693b72a50c7116db18d6497cac52"], ["mining.notify", "ae6812eb4cd7735a302a8a9dd95cf71f"]], "08000002", 4], "error": null}}\n'.format(id=id))

        return response

    def create_mining_notify_response(self, id):

        transactions_string = json.dumps(self.transactions)

        # response = ('{{"id": {id},"method": "mining.notify", "params": ["bf", "{prevhash}", "{coinbase1}", "{coinbase2}", {transactions}, "{version}", "{nbits}", "{ntime}", false ],"error": null}}\n'.format(id=id, prevhash="000000000000015f416afc2a44461adb178764a4fb45e5935c0a5717edf451a8", coinbase1="0400001059124d696e656420627920425443204775696c640800000037", coinbase2="05f1f0c7fc25005e7c6e56805130b4d540125a8d09f81ec3da621f99ee5d15c1", transactions=transactions_string, version="00000002", nbits="1a01aa3d", ntime=1368328721))
        response = (
            '{{"id": {id},"method": "mining.notify", "params": ["00123456789", "{prevhash}", "{coinbase1}", "{coinbase2}", {transactions}, "{version}", "{nbits}", "{ntime}", true ],"error": null}}\n'.format(
                id=id, prevhash=self.job_data['prevhash'], coinbase1=self.job_data['coinbase1'],
                coinbase2=self.job_data['coinbase2'], transactions=transactions_string,
                version=int(self.job_data['version']).to_bytes(4, byteorder='big').hex(), nbits=self.job_data['nbits'],
                ntime=self.job_data['ntime']))
        # response = ('{{"id": {id},"method": "mining.notify", "params": ["bf", "{prevhash}", "{coinbase}", {transactions}, "{version}", "{nbits}", "{ntime}", false ],"error": null}}\n'.format(id=id, prevhash=self.job_data['prevhash'], coinbase=self.job_data['coinbase1']+self.job_data['coinbase2'], transactions=transactions_string, version=self.job_data['version'], nbits=self.job_data['nbits'], ntime=self.job_data['ntime']))
        return response

    def create_mining_set_difficulty_response(self, id, difficulty):
        response = ('{{"id": {id}, "method": "mining.set_difficulty", "params": [{difficulty}]}}\n'.format(id=id,
                                                                                                           difficulty=difficulty))

        return response

    def create_mining_set_extranonce_response(self, id, extranonce1, extranonce2_size):
        response = (
            '{{"id": {id}, "method": "mining.set_extranonce", "params": [{extranonce1}, {extranonce2_size}]}}\n'.format(
                id=id, extranonce1=extranonce1, extranonce2_size=extranonce2_size))
        return response

    def handle_mining_get_transactions(self, id):
        transactions = self.process.select_random_transactions()  # Obtener las transacciones desde la base de datos
        response = (
            '{{"result": {transactions}, "error": null, "id": null}}\n'.format(id=id, transactions=transactions))
        return response

    def handle_mining_multi_version(self, id):
        # response = ('{{"id": {id}, "result": true, "error": null}}\n'.format(id=id))
        response = (
            '{{"id": {id}, "result": null, "error": [20, "Multi-version mining not supported", null]}}\n'.format(id=id))
        return response

    async def handle_mining_submit(self, id, extranonce2, ntime, nonce):
        self.is_sent_rpc = False
        # Verificar si el resultado es válido
        submission = await self.process.block_validate(self.coinbase_message, self.transactions, self.merkleroot,
                                                       extranonce2, ntime, nonce)
        if submission is not False:
            print(submission)
            # self.is_sent_rpc = await BlockTemplateFetcher.submitblock(submission)
            self.is_sent_rpc = True

            response = ('{{"id": {id}, "result": true, "error": null}}\n'.format(id=id))
        else:
            response = ('{{"id": {id}, "result": false, "error": "Invalid result"}}\n'.format(id=id))

        return response

    def handle_mining_authorize(self, id, worker, password):
        # Verificar las credenciales del trabajador
        # if self.verify_worker_credentials(worker, password) is True:
        response = ('{{"id": {id},"result": true,"error": null}}\n'.format(id=id))
        return response

    def verify_worker_credentials(self, worker, password):
        if worker == Config.get_worker() and password == Config.get_worker_password():
            return True
        return False

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        asyncio.create_task(self.handle_data(data))

    async def handle_data(self, data):
        print("Datos recibidos:", data)
        message = json.loads(data)  # Decodificar los datos binarios a una cadena y luego a un diccionario
        response = await self.handle_stratum_v1(message)
        self.send(response)
        if self.is_sent_rpc is True:
            self.transport.close()
            self.is_sent_rpc = False
            return

    def send(self, response):
        self.transport.write(response.encode('utf-8'))

    async def stop_server_after_timeout(self, server, seconds):
        await asyncio.sleep(seconds)
        server.close()
        await server.wait_closed()
        return

    async def run_server(self, process, coinbase_message, transactions, merkleroot, job_data):
        loop = asyncio.get_running_loop()

        server = await loop.create_server(
            lambda: StratumProtocol(process, coinbase_message, transactions, merkleroot, job_data),
            '0.0.0.0', 3333)

        loop.create_task(self.stop_server_after_timeout(server, 300))


        try:
            async with server:
                await server.serve_forever()
        except asyncio.CancelledError:
            print("Server was cancelled")
        except Exception as e:
            print(f"An error occurred: {e}")