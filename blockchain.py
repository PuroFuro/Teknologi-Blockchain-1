import hashlib
import json
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.create_block(previous_hash='0')

    def create_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.mempool,
            'previous_hash': previous_hash
        }
        self.mempool = []
        self.chain.append(block)
        return block

    def add_transaction(self, tx):
        self.mempool.append(tx)

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def last_block(self):
        return self.chain[-1]