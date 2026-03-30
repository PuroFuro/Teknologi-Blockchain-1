import hashlib
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def hash_data(data):
    """
    Mengubah data menjadi hash SHA-256
    """
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


def verify_signature(public_key_pem, data, signature):
    """
    Verifikasi digital signature
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode()
        )

        public_key.verify(
            signature,
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True

    except InvalidSignature:
        return False
    except Exception:
        return False


def format_key(key_str):
    """
    Membersihkan format public key (opsional)
    """
    return key_str.strip()