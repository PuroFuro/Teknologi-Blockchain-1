from blockchain_node.transaction import Transaction
from blockchain_node.wallet import Wallet


def main():
    node1 = Wallet("Node1")
    node2 = Wallet("Node2")
    node3 = Wallet("Node3")

    print("=== Real Transaction ===")
    real_tx = Transaction(
        sender=node1.get_public_key_pem(),
        receiver=node2.get_public_key_pem(),
        amount=1,
    )
    real_tx.sign_transaction(node1.private_key)
    print("Sender claims to be: Node1")
    print("Signed by: Node1 private key")
    print(f"Valid? {real_tx.verify_transaction()}")
    print()

    print("=== Fake Transaction ===")
    fake_tx = Transaction(
        sender=node1.get_public_key_pem(),
        receiver=node2.get_public_key_pem(),
        amount=1,
    )
    fake_tx.sign_transaction(node3.private_key)
    print("Sender claims to be: Node1")
    print("Signed by: Node3 private key")
    print(f"Valid? {fake_tx.verify_transaction()}")
    print()

    print("=== Tampered Transaction ===")
    tampered_tx = Transaction(
        sender=node1.get_public_key_pem(),
        receiver=node2.get_public_key_pem(),
        amount=1,
    )
    tampered_tx.sign_transaction(node1.private_key)
    tampered_tx.amount = 100
    print("Original transaction was signed for amount: 1")
    print("Amount was changed after signing to: 100")
    print(f"Valid? {tampered_tx.verify_transaction()}")


if __name__ == "__main__":
    main()
