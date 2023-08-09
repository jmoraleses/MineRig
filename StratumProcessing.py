import hashlib
import random
import struct
from binascii import unhexlify
from Config import *


class StratumProcessing:

    def __init__(self, coin, block_template_fetcher):

        self.coin = coin
        self.target = self.block_bits2target(block_template_fetcher['bits'])
        self.version = block_template_fetcher['version']
        self.prevhash = block_template_fetcher['previousblockhash']
        self.transactions = block_template_fetcher['transactions']
        self.fee = block_template_fetcher['coinbasevalue']
        self.nbits = block_template_fetcher['bits']
        self.ntime = block_template_fetcher['curtime']
        self.height = block_template_fetcher['height']
        self.merkleroot = None
        self.nonce = None
        self.hash = None

    def bitcoinaddress2hash160(self, addr):
        """
        Convert a Base58 Bitcoin address to its Hash-160 ASCII hex string.
        Args:
            addr (string): Base58 Bitcoin address
        Returns:
            string: Hash-160 ASCII hex string
        """

        table = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

        hash160 = 0
        addr = addr[::-1]
        for i, c in enumerate(addr):
            hash160 += (58 ** i) * table.find(c)

        # Convert number to 50-byte ASCII Hex string
        hash160 = "{:050x}".format(hash160)

        # Discard 1-byte network byte at beginning and 4-byte checksum at the end
        return hash160[2:50 - 8]

    def int2lehex(self, value, width):
        """
        Convierte un entero sin signo en una cadena ASCII hexagonal en orden pequeño.
        Args:
            value (int): valor
            width (int): ancho de byte
        Returns:
            string: cadena ASCII hexagonal
        """

        return value.to_bytes(width, byteorder='little').hex()

    def block_bits2target(self, bits):
        """
        Convert compressed target (block bits) encoding to target value.
        Arguments:
            bits (string): compressed target as an ASCII hex string
        Returns:
            bytes: big endian target
        """

        # Bits: 1b0404cb
        #       1b          left shift of (0x1b - 3) bytes
        #         0404cb    value
        bits = bytes.fromhex(bits)
        shift = bits[0] - 3
        value = bits[1:]

        # Shift value to the left by shift
        target = value + b"\x00" * shift
        # Add leading zeros
        target = b"\x00" * (32 - len(target)) + target

        return target

    def tx_compute_merkle_root(self, tx_hashes):
        """
        Compute the Merkle Root of a list of transaction hashes.
        Arguments:
            tx_hashes (list): list of transaction hashes as ASCII hex strings
        Returns:
            string: merkle root as a big endian ASCII hex string
        """

        # Convert list of ASCII hex transaction hashes into bytes
        # tx_hashes = [bytes.fromhex(tx_hash["hash"])[::-1] for tx_hash in transactions]
        tx_hashes = [bytes.fromhex(tx_hash)[::-1] for tx_hash in tx_hashes]

        # Iteratively compute the merkle root hash
        while len(tx_hashes) > 1:
            # Duplicate last hash if the list is odd
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])

            tx_hashes_new = []

            for i in range(len(tx_hashes) // 2):
                # Concatenate the next two
                concat = tx_hashes.pop(0) + tx_hashes.pop(0)
                # Hash them
                concat_hash = hashlib.sha256(hashlib.sha256(concat).digest()).digest()
                # Add them to our working list
                tx_hashes_new.append(concat_hash)

            tx_hashes = tx_hashes_new
        # print(tx_hashes[0][::-1].hex())
        # Format the root in big endian ascii hex
        return str(tx_hashes[0][::-1].hex())

    def block_compute_raw_hash(self, header):
        """
        Compute the raw SHA256 double hash of a block header.
        Arguments:
            header (bytes): block header
        Returns:
            bytes: block hash
        """

        return hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1]

    def tx_make_coinbase(self, coinbase_script):
        pubkey_script = "76" + "a9" + "14" + self.bitcoinaddress2hash160(get_wallet_address()) + "88" + "ac"
        coinbase_script = self.tx_encode_coinbase_height(self.height) + coinbase_script
        tx = "01000000" + "01" + "0" * 64 + "ffffffff" + self.int2varinthex(
            len(coinbase_script) // 2) + coinbase_script + "ffffffff" + "01" + self.int2lehex(self.fee,8) + \
             self.int2varinthex(len(pubkey_script) // 2) + pubkey_script + "00000000"
        return tx

    def block_make_header(self):
        header = b""
        header += struct.pack("<L", self.version)
        header += bytes.fromhex(self.prevhash)[::-1]
        header += bytes.fromhex(self.merkleroot)[::-1]
        header += struct.pack("<L", self.ntime)
        header += bytes.fromhex(self.nbits)[::-1]
        header += struct.pack("<L", self.nonce)
        return header

    def int2varinthex(self, value):
        """
        Convierte un entero sin signo en una cadena ASCII hexagonal varint en orden pequeño.
        Args:
            value (int): valor
        Returns:
            string: cadena ASCII hexagonal
        """

        if value < 0xfd:
            return self.int2lehex(value, 1)
        elif value <= 0xffff:
            return "fd" + self.int2lehex(value, 2)
        elif value <= 0xffffffff:
            return "fe" + self.int2lehex(value, 4)
        else:
            return "ff" + self.int2lehex(value, 8)

    def to_coinbase_script(self, message):
        coinbase_byte = message.encode('ascii')
        scriptsig = unhexlify(coinbase_byte).hex()
        return scriptsig

    def tx_encode_coinbase_height(self, height):
        """
        Codifica la altura de coinbase, según BIP 34:
        https://github.com/bitcoin/bips/blob/master/bip-0034.mediawiki
        Argumentos:
            height (int): altura del bloque minado
        Devoluciones:
            string: altura codificada como una cadena ASCII hexagonal
        """

        width = (height.bit_length() + 7) // 8

        return bytes([width]).hex() + self.int2lehex(height, width)

    def block_make_submit(self, transactions):
        """
        Format a solved block into the ASCII hex submit format.
        Arguments:
            block (dict): block template with 'nonce' and 'hash' populated
        Returns:
            string: block submission as an ASCII hex string
        """

        submission = ""

        # Block header
        submission += self.block_make_header().hex()
        # Number of transactions as a varint
        submission += self.int2varinthex(len(transactions))
        # Concatenated transactions data
        for tx in transactions:
            submission += tx['data']

        return submission

    def select_random_transactions(self):
        """Selecciona transacciones hasta que el tamaño total esté entre 220,000 y 280,000 bytes."""

        # Límites de tamaño en bytes
        min_size_limit = random.randint(130, 240) * 1024  # 220 KB
        max_size_limit = random.randint(240, 300) * 1024  # Valor aleatorio entre 280 KB y 360 KB

        # Mezcla las transacciones para garantizar un orden aleatorio
        random.shuffle(self.transactions)

        # Transacciones seleccionadas
        selected_transactions = []
        # Tamaño total de las transacciones seleccionadas
        total_size = 0

        for transaction in self.transactions:
            transaction_size = transaction['weight']
            projected_size = total_size + transaction_size
            # Agrega la transacción si el tamaño proyectado está dentro de los límites
            if min_size_limit <= projected_size <= max_size_limit:
                selected_transactions.append(transaction)
                total_size += transaction_size
            # Si no hemos alcanzado el tamaño mínimo, agrega la transacción incluso si excede el tamaño máximo
            elif total_size < min_size_limit:
                selected_transactions.append(transaction)
                total_size += transaction_size
            # Una vez que hemos alcanzado o superado el tamaño mínimo, podemos dejar de agregar transacciones
            elif total_size >= min_size_limit:
                break

        self.transactions = selected_transactions
        return selected_transactions

    def create_job_stratum(self, protocol_version):

        # Seleccionar transacciones aleatorias
        transactions = self.select_random_transactions(self.transactions)

        # Crear la transacción coinbase
        coinbase_tx = {}
        transactions.insert(0, coinbase_tx)
        coinbase_message = ('SOLO Mined').encode().hex()
        coinbase_script = self.to_coinbase_script(coinbase_message) + self.int2lehex(0, 4)  # extranonce
        coinbase1 = self.tx_make_coinbase(coinbase_script)

        # Crear la segunda parte de la transacción coinbase
        coinbase2 = "0"

        # Crear la raíz Merkle de las transacciones
        merkle = []
        for tx in transactions:
            while tx.get('hash') is None:
                pass
            merkle.append(tx['hash'])
        self.merkleroot = self.tx_compute_merkle_root(merkle)

        # Crear el trabajo de minería
        job_id = random.randint(0, 1000000)

        clean_jobs = True

        # Devolver las variables importantes
        if protocol_version == 2:
            return {
                'job_id': job_id,
                'prevhash': self.prevhash,
                'coinb1': coinbase1,
                'coinb2': coinbase2,
                'merkle_branches': self.merkleroot,
                'version': self.version,
                'nbits': self.nbits,
                'ntime': self.ntime,
                'clean_jobs': clean_jobs
            }
        else:
            return {
                'job_id': job_id,
                'version': self.version,
                'prevhash': self.prevhash,
                'coinbase1': coinbase1,
                'transactions': transactions,
                'merkle_root': self.merkleroot,
                'nbits': self.nbits,
                'ntime': self.ntime,
                'clean_jobs': clean_jobs
            }

    #
    # def create_job_stratum(self, protocol_version, prevhash, version, nbits, ntime):
    #     # Seleccionar transacciones aleatorias
    #     transactions = self.select_random_transactions(self.transactions)
    #
    #     # Crear la transacción coinbase
    #     coinbase_tx = {}
    #     transactions.insert(0, coinbase_tx)
    #     coinbase_message = ('SOLO Mined').encode().hex()
    #     coinbase_script = self.to_coinbase_script(coinbase_message) + self.int2lehex(0, 4)  # extranonce
    #     coinbase1 = self.tx_make_coinbase(coinbase_script)
    #
    #     # Crear la segunda parte de la transacción coinbase
    #     coinbase2 = "0"
    #
    #     # Crear la raíz Merkle de las transacciones
    #     merkle = []
    #     for tx in transactions:
    #         while tx.get('hash') is None:
    #             pass
    #         merkle.append(tx['hash'])
    #     merkleroot = self.tx_compute_merkle_root(merkle)
    #
    #     # Crear el trabajo de minería
    #     job_id = random.randint(0, 1000000)
    #
    #     clean_jobs = True
    #
    #     # Devolver las variables importantes
    #     if protocol_version == 2:
    #         return {
    #             'job_id': job_id,
    #             'prevhash': prevhash,
    #             'coinb1': coinbase1,
    #             'coinb2': coinbase2,
    #             'merkle_branches': merkleroot,
    #             'version': version,
    #             'nbits': nbits,
    #             'ntime': ntime,
    #             'clean_jobs': clean_jobs
    #         }
    #     else:
    #         return {
    #             'job_id': job_id,
    #             'version': version,
    #             'prevhash': prevhash,
    #             'coinbase1': coinbase1,
    #             'transactions': transactions,
    #             'merkle_root': merkleroot,
    #             'nbits': nbits,
    #             'ntime': ntime,
    #             'clean_jobs': clean_jobs
    #         }

    def block_validate(self, ntime, nonce):
        self.ntime = ntime
        merkle = []
        for tx in self.transactions:
            while tx.get('hash') is None:
                pass
            merkle.append(tx['hash'])
        # print(merkle)
        self.merkleroot = self.tx_compute_merkle_root(merkle)
        block_header_raw = self.block_make_header()
        block_header = block_header_raw[0:76] + nonce.to_bytes(4, byteorder='little')
        block_hash = self.block_compute_raw_hash(block_header)
        if block_hash < self.target:
            self.nonce = nonce
            self.hash = block_hash.hex()
            print("Solved a block! Block hash: {}".format(self.hash))
            submission = self.block_make_submit(self.transactions)
            # result = self.rpc_submitblock(submission)
            return submission
        else:
            print("Bloque no aceptado")
        return False
