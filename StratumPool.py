import asyncio
import socket

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumClient import StratumClient
from StratumProcessing import StratumProcessing


class StratumPool:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []

    async def start(self):
        # Crear instancia de BlockTemplateFetcher
        fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                       Config.get_bitcoin_password())

        # Bucle principal
        while True:

            # Crear servidor Stratum
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

                server_socket.bind((self.host, self.port))
                server_socket.listen()
                print(f"Listening on {self.host}:{self.port}")

                # Obtener plantilla de bloque en segundo plano
                template = await fetcher.get_block_template()

                if template is not None:

                    # Aceptar conexión entrante
                    client_socket, client_address = server_socket.accept()
                    print(f"Accepted connection from {client_address}\n")

                    client_ip, client_port = client_address
                    print(f"ip: {client_ip} port: {client_port}\n")

                    # Crear trabajo a partir de la plantilla
                    process = StratumProcessing(Config.bitcoin, template)

                    client = StratumClient(client_socket, client_address, process)
                    self.clients.append(client)

                    # Ejecutar cliente en segundo plano
                    await asyncio.create_task(client.run())

                    client.close()
                    self.clients.remove(client)

    def stop(self):
        for client in self.clients:
            client.close()


if __name__ == '__main__':
    pool = StratumPool(Config.get_url_stratum(), int(Config.get_port_stratum()))
    asyncio.run(pool.start())

