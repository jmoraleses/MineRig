import asyncio
import socket

import Config
from StratumClient import StratumClient
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumMessage import StratumMessage
from StratumProcessing import StratumProcessing
from StratumSession import StratumSession


class StratumPool:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []

    async def start(self):
        # Crear instancia de BlockTemplateFetcher
        fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                       Config.get_bitcoin_password())

        # Crear servidor Stratum
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Listening on {self.host}:{self.port}")

            # Bucle principal
            while True:

                # Obtener plantilla de bloque en segundo plano
                template = await fetcher.get_block_template()

                # Aceptar conexión entrante
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from {client_address}")

                # Crear trabajo a partir de la plantilla
                process = StratumProcessing(Config.bitcoin, template)

                client = StratumClient(client_socket, client_address[0], process)
                self.clients.append(client)
                client.run()

                # Crear sesión Stratum
                # session = StratumSession(client)


                job = process.create_job_stratum(protocol_version=1)
                print(job)

                # # Crear mensaje mining.notify
                # message = StratumMessage(
                #     method='mining.notify',
                #     params=[
                #         job.job_id,
                #         job.prevhash,
                #         job.coinb1,
                #         job.coinb2,
                #         job.merkle_branches,
                #         job.version,
                #         job.nbits,
                #         job.ntime,
                #         True
                #     ]
                # )
                # print(message)
                #
                # # Enviar mensaje mining.notify a todos los clientes
                # for client in self.clients:
                #     client.send(message)

                # Ejecutar cliente en segundo plano
                asyncio.create_task(client.run())

    def stop(self):
        for client in self.clients:
            client.close()


if __name__ == '__main__':
    pool = StratumPool('localhost', 3333)
    asyncio.run(pool.start())
