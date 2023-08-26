import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
import Config
from BlockTemplateFetcher import BlockTemplateFetcher
from StratumProcessing import StratumProcessing
import tensorflow as tf
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

def process_and_submit(process, model, time_block):
    submission = process.create_job_machine(model, time_block)
    # print(f"start {start_extranonce} increment: {increment_extranonce}")
    return submission

def task(args):
    process = args
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_and_submit(process))
    loop.close()
    return result


def generate_combinations(base_string, total_combinations):
    combinations = []
    for i in range(total_combinations):
        hex_counter = hex(i)[2:]
        hex_counter_padded = hex_counter.zfill(8)

        combined_string = bytes.fromhex(base_string).hex() + bytes.fromhex(hex_counter_padded).hex()
        combinations.append(combined_string)

    return np.array(combinations)


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
        time_block = template['curtime']
    except:
        print("Bitcoin Core no encontrado. ¿está encendido?")
    ini = time.time()
    i = 0
    num_processes = 100  # Número de tareas que deseas ejecutar

    process = StratumProcessing(Config.bitcoin, template)
    model = tf.keras.models.load_model("model_lineal.h5")
    # modelo_time = tf.keras.models.load_model("modelo_time.h5")
    # increment_extranonce = 1000
    # coinbase_message = ('SOLO Mined').encode().hex()
    # list_coinbase_script = ParallelizationGPU.concat_extranonce(bytes.fromhex(process.to_coinbase_script(coinbase_message)), num_processes*increment_extranonce, 0)
    # list_coinbase_script = generate_combinations(process.to_coinbase_script(coinbase_message), num_processes*increment_extranonce)
    print("start")
    while True:

        if template is not None:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=20) as executor:
                tasks = [loop.run_in_executor(executor, process_and_submit, process, model, time_block) for _ in range(num_processes)]
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
            ini = time.time()
            clear_console()
            print(f"{my_time:.2f}segundos")
            print(f"{((i*(16**8*num_processes*600*15)/(int(my_time)*1000000000000)))} Thashes/s")
            template = await fetcher.get_block_template()
            process.set_template(Config.bitcoin, template)
            time_block = template['curtime']
            print(time_block)
            i = 0



if __name__ == "__main__":
    asyncio.run(main())
