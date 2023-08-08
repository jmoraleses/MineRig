from StratumMessage import StratumMessage


class StratumSession:
    def __init__(self, client):
        self.client = client

    def subscribe(self):
        message = StratumMessage('mining.subscribe')
        self.client.send(message.to_json())
        response = self.client.receive()
        return response['result']

    def authorize(self, username, password):
        message = StratumMessage('mining.authorize', [username, password])
        self.client.send(message.to_json())
        response = self.client.receive()
        return response['result']

    def submit(self, job_id, nonce, result):
        message = StratumMessage('mining.submit', [self.client.username, job_id, nonce, result])
        self.client.send(message.to_json())
        response = self.client.receive()
        return response['result']

