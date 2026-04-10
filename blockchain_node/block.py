import datetime
import hashlib
import json


class Block:
    def __init__(
        self,
        index,
        transactions,
        previous_hash,
        timestamp=None,
        nonce=0,
        block_hash=None,
    ):
        self.index = index
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat() + "Z"
        self.transactions = [
            transaction if isinstance(transaction, dict) else transaction.to_dict()
            for transaction in transactions
        ]
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = block_hash or self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
        }
        block_string = json.dumps(
            block_data,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            transactions=data["transactions"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            block_hash=data["hash"],
        )
