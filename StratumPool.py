import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor

import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumProcessing import StratumProcessing

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
    try:
        template = await fetcher.get_block_template()
        if template is not None:
            process = StratumProcessing(Config.bitcoin, template)
    except:
        print("Bitcoin Core no encontrado. ¿está encendido?")
    ini = time.time()
    i = 0
    while True:

        num_processes = 10  # Número de tareas que deseas ejecutar
        if template is not None:
            loop = asyncio.get_running_loop()
            with ProcessPoolExecutor(max_workers=20) as executor:
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
        if my_time > 10:
            template = await fetcher.get_block_template()
            process.set_template(Config.bitcoin, template)
            ini = time.time()
            clear_console()
            print(f"{my_time:.2f}segundos")
            print(f"{((i*(16**8*16**8*num_processes*10*2)/(int(my_time)*1000000000000000000)))} Ehashes/s")
            i = 0


if __name__ == "__main__":
    asyncio.run(main())
