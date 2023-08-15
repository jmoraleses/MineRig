import asyncio
import time
import concurrent.futures
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

def process_and_submit(bitcoin_config, template, fetcher, process):
    process.set_template(bitcoin_config, template)
    submission = process.create_job_probe()
    if submission is not False:
        fetcher.submitblock(submission)
        return True
    return False

async def main():
    # client = StratumClient()
    # server = await asyncio.start_server(client.handle_miner, '0.0.0.0', 3333)
    # addr = server.sockets[0].getsockname()
    # print(f'Sirviendo en {addr}')
    # async with server:
    #     await server.serve_forever()
    template = None
    fetcher = BlockTemplateFetcher(Config.get_bitcoin_url(), Config.get_bitcoin_username(),
                                   Config.get_bitcoin_password())

    template = await fetcher.get_block_template()
    process = StratumProcessing(Config.bitcoin, template)

    while True:
        if template is not None:
            template = await fetcher.get_block_template()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(process_and_submit, Config.bitcoin, template, fetcher, process)
                result = future.result()
                if result:
                    print("Minado!")


if __name__ == '__main__':
    asyncio.run(main())
