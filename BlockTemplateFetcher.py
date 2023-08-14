import json
import random
import time

import requests

class BlockTemplateFetcher:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.template = None
        self.last_update = None

    async def rpc(self, method, params):
        rpc_id = random.getrandbits(32)
        payload = json.dumps({"id": rpc_id, "method": method, "params": params}).encode()
        # auth = base64.encodebytes((RPC_USER + ":" + RPC_PASS).encode()).decode().strip()
        headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        msg = requests.request("POST", self.url, data=payload, headers=headers, auth=(self.username, self.password))
        response = json.loads(msg.text)

        if response['id'] != rpc_id:
            raise ValueError("Invalid response id: got {}, expected {:d}".format(response['id'], rpc_id))
        elif response['error'] is not None:
            raise ValueError("RPC error: {:s}".format(json.dumps(response['error'])))
        return response['result']

    async def get_block_template(self):
        time.sleep(0.5)
        while True:
            try:
                return await self.rpc("getblocktemplate", [{"rules": ["segwit"]}])
            except ValueError:
                return {}


    async def submitblock(self, params):
        result = None
        if params is not False:
            result = await self.rpc("submitblock", [params])
        if result:
            return True
        return False
