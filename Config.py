import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

def get_bitcoin_url():
    return config['Bitcoin']['url']

def get_bitcoin_username():
    return config['Bitcoin']['username']

def get_bitcoin_password():
    return config['Bitcoin']['password']

def get_refresh_interval():
    return int(config['Bitcoin']['refresh_interval'])

def get_worker():
    return config['Pool']['WORKER']

def get_url_stratum():
    return config['Pool']['URL_STRATUM']

def get_port_stratum():
    return config['Pool']['PORT_STRATUM']

def get_worker_password():
    return config['Pool']['PASS_WORKER']

def get_wallet_address():
    return config['Wallet']['address']

def get_extranonce1():
    return config['Stratum']['extranonce1']

def get_extranonce2():
    return config['Stratum']['extranonce2']

def get_difficulty_target():
    return int(config['Stratum']['diff_1_target'], 0)

def get_nonce():
    return config['Stratum']['nonce']

def create_coin(name, symbol, algorithm):
    return {'name': name, 'symbol': symbol, 'algorithm': algorithm}

bitcoin = create_coin('Bitcoin', 'BTC', 'SHA-256')
litecoin = create_coin('Litecoin', 'LTC', 'Scrypt')
ethereum = create_coin('Ethereum', 'ETH', 'Ethash')