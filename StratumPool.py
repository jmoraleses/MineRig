import asyncio
import multiprocessing
import os
import threading
import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Pool

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumClient import StratumClient
from StratumProcessing import StratumProcessing
import copy

stop_server = False

def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # Si la máquina es Windows
        command = 'cls'
    os.system(command)


async def fetch_block_template():
    await asyncio.sleep(0.5)
    # Crear instancia de BlockTemplateFetcher
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())
    # Obtener la plantilla de bloque
    template = await fetcher.get_block_template()
    return template, fetcher

def process_and_submit(process):
    submission = process.create_job_probe()
    return submission

def task(args):
    process = args
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_and_submit(process))
    loop.close()
    return result

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
    ini = time.time()
    i = 0
    while True:

        num_processes = 20  # Número de tareas que deseas ejecutar
        if template is not None:
            loop = asyncio.get_event_loop()
            with ProcessPoolExecutor(max_workers=num_processes) as executor:
                tasks = [loop.run_in_executor(executor, process_and_submit, process) for _ in range(num_processes)]
                results = await asyncio.gather(*tasks)

                for submission_data in results:
                    if submission_data is not False:
                        submission_result = await fetcher.submitblock(submission_data)
                        print(submission_result)
                        print("Mined!")

        i += 1
        fin = time.time()
        my_time = fin - ini
        if my_time > 6:
            template = await fetcher.get_block_template()
            process.set_template(Config.bitcoin, template)
            ini = time.time()
            clear_console()
            print(f"{((i*(3213492224*num_processes)/6000000000))} Ghashes/s")
            i = 0


if __name__ == "__main__":
    asyncio.run(main())
