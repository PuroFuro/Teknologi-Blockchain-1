import binascii
import hashlib
import json
from decimal import Decimal, InvalidOperation

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .constants import SYSTEM_SENDER


class Transaction:
    def __init__(self, sender, receiver, amount, signature="", transaction_hash=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)
        self.signature = signature or ""
        self.transaction_hash = transaction_hash or self.calculate_transaction_hash()

    @staticmethod
    def _normalize_amount(amount):
        try:
            normalized = Decimal(str(amount)).normalize()
        except InvalidOperation as error:
            raise ValueError("Amount must be numeric.") from error
        return format(normalized, "f")

    def _payload(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self._normalize_amount(self.amount),
        }

    def calculate_transaction_hash(self):
        payload_string = json.dumps(
            self._payload(),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload_string.encode("utf-8")).hexdigest()

    def sign_transaction(self, private_key):
        self.transaction_hash = self.calculate_transaction_hash()
        sig_bytes = private_key.sign(
            self.transaction_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        self.signature = binascii.hexlify(sig_bytes).decode("utf-8")

    def verify_transaction(self):
        if self.transaction_hash != self.calculate_transaction_hash():
            return False

        if self.sender == SYSTEM_SENDER:
            return True

        if not self.signature:
            return False

        try:
            public_key = serialization.load_pem_public_key(self.sender.encode("utf-8"))
            sig_bytes = binascii.unhexlify(self.signature)
            public_key.verify(
                sig_bytes,
                self.transaction_hash.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def is_amount_positive(self):
        return self.amount > 0

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "signature": self.signature,
            "transaction_hash": self.transaction_hash,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            amount=data["amount"],
            signature=data.get("signature", ""),
            transaction_hash=data.get("transaction_hash"),
        )
