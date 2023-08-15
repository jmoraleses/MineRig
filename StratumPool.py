import asyncio
import threading
import time
import asyncio
from multiprocessing import Process

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumClient import StratumClient
from StratumProcessing import StratumProcessing
import copy

stop_server = False


async def fetch_block_template():
    await asyncio.sleep(0.5)
    # Crear instancia de BlockTemplateFetcher
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())
    # Obtener la plantilla de bloque
    template = await fetcher.get_block_template()
    return template, fetcher


async def process_and_submit(bitcoin_config, template, process, fetcher):
    process.set_template(bitcoin_config, template)
    submission = await process.create_job_probe()
    if submission is not False:
        result = await fetcher.submitblock(submission)
        print(result)

async def main():
    # Minería con stratum
    # client = StratumClient()
    # server = await asyncio.start_server(client.handle_miner, '0.0.0.0', 3333)
    # addr = server.sockets[0].getsockname()
    # print(f'Sirviendo en {addr}')
    # async with server:
    #     await server.serve_forever()

    # Minería con cpu
    template = None
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())
    template = await fetcher.get_block_template()
    process = StratumProcessing(Config.bitcoin, template)
    while True:
        if template is not None:
            template = await fetcher.get_block_template()
            process.set_template(Config.bitcoin, template)

            num_processes = 5  # Número de tareas que deseas ejecutar
            tasks = []

            # Crear y agregar las tareas a la lista
            for _ in range(num_processes):
                task = asyncio.create_task(process_and_submit(Config.bitcoin, template, process, fetcher))
                tasks.append(task)

            # Esperar a que todas las tareas terminen
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
