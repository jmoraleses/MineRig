import json


class StratumMessage:
    def __init__(self, method, params=None, id=None):
        self.method = method
        self.params = params or []
        self.id = id or 1

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'method': self.method,
            'params': self.params
        })
