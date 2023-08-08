import json
from StratumSession import StratumSession


class StratumClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.session = StratumSession(self)

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
            self.handle_stratum_message(message)

    def handle_stratum_message(self, message):
        version = message.get('version')
        if version == 'Stratum/1.0.0':
            return self.handle_stratum_v1_message(message)
        elif version == 'Stratum/2.0.0':
            return self.handle_stratum_v2_message(message)
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

    def handle_stratum_v2_message(self, message):
        method = message.get('method')
        params = message.get('params')

        if method == 'mining.subscribe':
            # Procesar mensaje de suscripción
            job_id = 'some_job_id'
            coinbase_params = ['param1', 'param2', 'param3']
            response = {
                'jsonrpc': '2.0',
                'result': {
                    'job_id': job_id,
                    'params': coinbase_params
                },
                'id': params[0]
            }
        elif method == 'mining.authorize':
            # Procesar mensaje de autorización
            username = params[0]
            password = params[1]
            is_valid = True  # Validar usuario y contraseña
            response = {
                'jsonrpc': '2.0',
                'result': is_valid,
                'id': params[2]
            }
        elif method == 'mining.notify':
            # Procesar mensaje de notificación
            job_id = params[0]
            prev_hash = params[1]
            coinbase = params[2]
            merkle_branches = params[3]
            response = {
                'jsonrpc': '2.0',
                'result': True,
                'id': None
            }
            # Procesar trabajo
        elif method == 'mining.set_difficulty':
            # Procesar mensaje de establecimiento de dificultad
            difficulty = params[0]
            response = {
                'jsonrpc': '2.0',
                'result': True,
                'id': None
            }
            # Actualizar dificultad
        elif method == 'mining.set_extranonce':
            # Procesar mensaje de establecimiento de extranonce
            extranonce = params[0]
            response = {
                'jsonrpc': '2.0',
                'result': True,
                'id': None
            }
            # Actualizar extranonce
        elif method == 'mining.submit':
            # Procesar mensaje de envío de resultado de minería
            username = params[0]
            job_id = params[1]
            nonce = params[2]
            result = params[3]
            response = {
                'jsonrpc': '2.0',
                'result': True,
                'id': None
            }
            # Verificar resultado de minería
        else:
            # Método desconocido
            response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': 'Método desconocido'
                },
                'id': None
            }

        return response


    def handle_stratum_v1_message(self, message):
        method = message.get('method')
        params = message.get('params')

        if method == 'mining.subscribe':
            # Procesar mensaje de suscripción
            job_id = 'some_job_id'
            coinbase_params = ['param1', 'param2', 'param3']
            response = {
                'result': [job_id, coinbase_params],
                'error': None,
                'id': params[0]
            }
        elif method == 'mining.authorize':
            # Procesar mensaje de autorización
            username = params[0]
            password = params[1]
            is_valid = True  # Validar usuario y contraseña
            response = {
                'result': is_valid,
                'error': None,
                'id': params[2]
            }
        elif method == 'mining.notify':
            # Procesar mensaje de notificación
            job_id = params[0]
            prev_hash = params[1]
            coinbase = params[2]
            merkle_branches = params[3]
            response = {
                'result': True,
                'error': None,
                'id': None
            }
            # Procesar trabajo
        elif method == 'mining.set_difficulty':
            # Procesar mensaje de establecimiento de dificultad
            difficulty = params[0]
            response = {
                'result': True,
                'error': None,
                'id': None
            }
            # Actualizar dificultad
        elif method == 'mining.set_extranonce':
            # Procesar mensaje de establecimiento de extranonce
            extranonce = params[0]
            response = {
                'result': True,
                'error': None,
                'id': None
            }
            # Actualizar extranonce
        elif method == 'mining.submit':
            # Procesar mensaje de envío de resultado de minería
            username = params[0]
            job_id = params[1]
            nonce = params[2]
            result = params[3]
            response = {
                'result': True,
                'error': None,
                'id': None
            }
            # Verificar resultado de minería
        else:
            # Método desconocido
            response = {
                'result': None,
                'error': 'Método desconocido',
                'id': None
            }

        return response

    def generate_subscribe_response(self, job_id, coinbase_params):
        response = {
            'result': [job_id, coinbase_params],
            'error': None,
            'id': 1
        }

        return response


    def generate_subscribe_response_v2(self, message_id, job_id, difficulty, extranonce, coinbase_params):
        response = {
            'result': {
                'mining.notify': [message_id, job_id, coinbase_params, True],
                'mining.set_difficulty': [difficulty, message_id],
                'mining.set_extranonce': extranonce
            },
            'error': None,
            'id': 1
        }

        return response


    def generate_authorize_response(self, is_valid, error_message=None):
        if is_valid:
            result = True
            error = None
        else:
            result = None
            error = error_message

        response = {
            'result': result,
            'error': error,
            'id': 2
        }

        return response


    def generate_authorize_response_v2(self, is_valid, error_message=None):
        if is_valid:
            result = True
            error = None
        else:
            result = None
            error = error_message

        response = {
            'result': result,
            'error': error,
            'id': 2
        }

        return response


    def generate_notify_response(self, job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime):
        response = {
            'result': [job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime],
            'error': None,
            'id': 3
        }

        return response


    def generate_notify_response_v2(self, job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime):
        response = {
            'result': {
                'job_id': job_id,
                'prevhash': prevhash,
                'coinb1': coinb1,
                'coinb2': coinb2,
                'merkle_branch': merkle_branch,
                'version': version,
                'nbits': nbits,
                'ntime': ntime
            },
            'error': None,
            'id': 3
        }

        return response


    def generate_set_difficulty_response(self, difficulty):
        response = {
            'result': difficulty,
            'error': None,
            'id': 4
        }

        return response


    def generate_set_difficulty_response_v2(self, difficulty, message_id):
        response = {
            'result': [difficulty, message_id],
            'error': None,
            'id': 4
        }

        return response


    def generate_set_extranonce_response(self, extranonce):
        response = {
            'result': extranonce,
            'error': None,
            'id': 5
        }

        return response


    def generate_set_extranonce_response_v2(self, extranonce):
        response = {
            'result': extranonce,
            'error': None,
            'id': 5
        }

        return response
