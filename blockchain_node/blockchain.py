import hashlib
from urllib.parse import urlparse

from .block import Block
from .constants import (
    GENESIS_MESSAGE,
    GENESIS_TIMESTAMP,
    INITIAL_BALANCE,
    MINING_DIFFICULTY,
    MINING_REWARD,
    SYSTEM_SENDER,
)
from .transaction import Transaction


class Blockchain:
    def __init__(self):
        self.difficulty = MINING_DIFFICULTY
        self.pending_transactions = []
        self.chain = [self.init_genesis_block()]
        self.nodes = set()

    def init_genesis_block(self):
        genesis_previous_hash = hashlib.sha256(GENESIS_MESSAGE.encode("utf-8")).hexdigest()
        genesis_tx = Transaction(
            sender=SYSTEM_SENDER,
            receiver="Genesis",
            amount=0,
            signature="0",
        )
        return Block(
            index=0,
            transactions=[genesis_tx.to_dict()],
            previous_hash=genesis_previous_hash,
            timestamp=GENESIS_TIMESTAMP,
        )

    def get_latest_block(self):
        return self.chain[-1]

    def get_balance(self, public_key):
        balance = float(INITIAL_BALANCE)

        for block in self.chain:
            for tx in block.transactions:
                sender = tx["sender"]
                receiver = tx["receiver"]
                amount = float(tx["amount"])

                if sender == public_key:
                    balance -= amount
                if receiver == public_key:
                    balance += amount

        for tx in self.pending_transactions:
            if tx["sender"] == public_key:
                balance -= float(tx["amount"])

        return round(balance, 8)

    @staticmethod
    def normalize_node_address(node):
        parsed = urlparse(node)
        if not parsed.scheme or not parsed.netloc:
            return None
        return node.rstrip("/")

    def add_nodes(self, nodes):
        added_nodes = []
        for node in nodes:
            normalized = self.normalize_node_address(node)
            if normalized:
                self.nodes.add(normalized)
                added_nodes.append(normalized)
        return added_nodes

    def _has_pending_duplicate(self, transaction):
        for existing in self.pending_transactions:
            if (
                existing["transaction_hash"] == transaction.transaction_hash
                and existing["signature"] == transaction.signature
            ):
                return True
        return False

    def add_pending_transaction(self, transaction, allow_system=False):
        if transaction.sender == SYSTEM_SENDER and not allow_system:
            return False, "External transactions cannot claim SYSTEM as the sender."

        if transaction.sender != SYSTEM_SENDER and not transaction.is_amount_positive():
            return False, "Transaction amount must be greater than zero."

        if not transaction.verify_transaction():
            return False, "Cryptographic signature validation failed."

        if transaction.sender != SYSTEM_SENDER:
            current_balance = self.get_balance(transaction.sender)
            if current_balance < transaction.amount:
                return (
                    False,
                    f"Insufficient balance ({current_balance}) to complete the transaction.",
                )

        if self._has_pending_duplicate(transaction):
            return False, "Transaction is already in the mempool."

        self.pending_transactions.append(transaction.to_dict())
        return True, "Transaction added to the mempool."

    def mine_pending_transactions(self, miner_public_key):
        if not self.pending_transactions:
            return None

        reward_tx = Transaction(
            sender=SYSTEM_SENDER,
            receiver=miner_public_key,
            amount=MINING_REWARD,
        )
        block_transactions = [reward_tx.to_dict(), *self.pending_transactions]

        new_block = Block(
            index=len(self.chain),
            transactions=block_transactions,
            previous_hash=self.get_latest_block().hash,
        )
        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def chain_to_list(self):
        return [block.to_dict() for block in self.chain]

    def _confirmed_transaction_hashes(self):
        confirmed_hashes = set()
        for block in self.chain:
            for tx in block.transactions:
                tx_hash = tx.get("transaction_hash")
                if tx_hash:
                    confirmed_hashes.add(tx_hash)
        return confirmed_hashes

    def _trim_confirmed_pending_transactions(self):
        confirmed_hashes = self._confirmed_transaction_hashes()
        self.pending_transactions = [
            tx
            for tx in self.pending_transactions
            if tx.get("transaction_hash") not in confirmed_hashes
        ]

    def is_valid_chain_data(self, chain_data):
        if not chain_data:
            return False

        try:
            blocks = [Block.from_dict(block_data) for block_data in chain_data]
        except (KeyError, TypeError, ValueError):
            return False

        if blocks[0].to_dict() != self.init_genesis_block().to_dict():
            return False

        running_deltas = {}

        for index, block in enumerate(blocks):
            if block.index != index:
                return False

            if block.calculate_hash() != block.hash:
                return False

            if index == 0:
                continue

            previous_block = blocks[index - 1]
            if block.previous_hash != previous_block.hash:
                return False

            if not block.hash.startswith("0" * self.difficulty):
                return False

            reward_transactions = 0
            for tx_index, tx_data in enumerate(block.transactions):
                try:
                    transaction = Transaction.from_dict(tx_data)
                except (KeyError, TypeError, ValueError):
                    return False

                if not transaction.verify_transaction():
                    return False

                if transaction.sender == SYSTEM_SENDER:
                    reward_transactions += 1
                    if tx_index != 0 or transaction.amount != MINING_REWARD:
                        return False
                    running_deltas[transaction.receiver] = (
                        running_deltas.get(transaction.receiver, 0.0) + transaction.amount
                    )
                    continue

                if not transaction.is_amount_positive():
                    return False

                sender_balance = INITIAL_BALANCE + running_deltas.get(transaction.sender, 0.0)
                if sender_balance < transaction.amount:
                    return False

                running_deltas[transaction.sender] = (
                    running_deltas.get(transaction.sender, 0.0) - transaction.amount
                )
                running_deltas[transaction.receiver] = (
                    running_deltas.get(transaction.receiver, 0.0) + transaction.amount
                )

            if reward_transactions != 1:
                return False

        return True

    def replace_chain(self, chain_data):
        if len(chain_data) <= len(self.chain):
            return False

        if not self.is_valid_chain_data(chain_data):
            return False

        self.chain = [Block.from_dict(block_data) for block_data in chain_data]
        self._trim_confirmed_pending_transactions()
        return True
