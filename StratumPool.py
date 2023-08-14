import asyncio
import socket
import time

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumClient import StratumClient
from StratumProcessing import StratumProcessing

stop_server = False

async def fetch_block_template():
    await asyncio.sleep(0.5)
    # Crear instancia de BlockTemplateFetcher
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())
    # Obtener la plantilla de bloque
    template = await fetcher.get_block_template()
    return template, fetcher

async def main():
    # client = StratumClient()
    # server = await asyncio.start_server(client.handle_miner, '0.0.0.0', 3333)
    # addr = server.sockets[0].getsockname()
    # print(f'Sirviendo en {addr}')
    # async with server:
    #     await server.serve_forever()

    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(), Config.get_bitcoin_password())
    while True:
        template = await fetcher.get_block_template()

        process = StratumProcessing(Config.bitcoin, template)
        submission = process.create_job_probe()
        if submission is not False:
            fetcher.submitblock(submission)
            print("Minado!")


if __name__ == '__main__':
    asyncio.run(main())