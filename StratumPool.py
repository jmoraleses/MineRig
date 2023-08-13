import asyncio
import socket

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumClient import StratumClient
from StratumProcessing import StratumProcessing

stop_server = False
# class StratumPool:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.clients = []
#
#     async def start(self):
#
#         # Crear un bucle de eventos
#         # loop = asyncio.get_event_loop()
#         loop = asyncio.get_running_loop()
#
#
#         # Obtener la plantilla block_template en segundo plano
#         template, fetcher = await self.fetch_block_template()
#
#
#         # Crear servidor Stratum
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         server_socket.bind((self.host, self.port))
#         server_socket.listen()
#         print(f"Listening on {self.host}:{self.port}")
#         while not stop_server:
#
#             if template:
#
#                 # Aceptar conexión entrante
#                 client_socket, client_address = server_socket.accept()
#                 print(f"Accepted connection from {client_address}\n")
#
#                 client_ip, client_port = client_address
#                 print(f"ip: {client_ip} port: {client_port}\n")
#
#                 # Crear trabajo a partir de la plantilla
#                 process = StratumProcessing(Config.bitcoin, template)
#
#                 client = StratumClient(client_socket, process, fetcher)
#                 await client.run()
#
#                 # Cerrar socket cliente
#                 client_socket.close()
#
#         # Cerrar socket servidor
#         server_socket.close()

async def fetch_block_template():
    # Crear instancia de BlockTemplateFetcher
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())
    # Obtener la plantilla de bloque
    template = await fetcher.get_block_template()
    return template, fetcher


# async def main():
#     # Obtener el bucle de eventos de asyncio
#     # loop = asyncio.get_running_loop()
#     pool = StratumPool(Config.get_url_stratum(), int(Config.get_port_stratum()))
#     while True:
#         await pool.start()
#         # Revisar variable global para detenerse
#         if stop_server:
#             break


async def main():
    # pool = StratumPool(Config.get_url_stratum(), int(Config.get_port_stratum()))
    template, fetcher = await fetch_block_template()
    process = StratumProcessing(Config.bitcoin, template)
    client = StratumClient(process, fetcher)
    server = await asyncio.start_server(client.handle_miner, '0.0.0.0', 3333)

    addr = server.sockets[0].getsockname()
    print(f'Sirviendo en {addr}')

    async with server:
        await server.serve_forever()


asyncio.run(main())


if __name__ == '__main__':
    asyncio.run(main())