import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from flask import Flask, jsonify, request

from .blockchain import Blockchain
from .constants import MINING_REWARD
from .transaction import Transaction
from .wallet import Wallet


def http_get_json(url, timeout=3):
    with urllib_request.urlopen(url, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
        return response.status, json.loads(payload) if payload else {}


def http_post_json(url, payload, timeout=3):
    request_data = json.dumps(payload).encode("utf-8")
    outgoing_request = urllib_request.Request(
        url,
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib_request.urlopen(outgoing_request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
        return response.status, json.loads(payload) if payload else {}


def create_app(node_name):
    app = Flask(__name__)
    node_chain = Blockchain()
    identity = Wallet(name=node_name)

    @app.route("/profile", methods=["GET"])
    def get_profile():
        public_key = identity.get_public_key_pem()
        return jsonify(
            {
                "name": identity.name,
                "public_key": public_key,
                "private_key_managed": True,
                "balance": node_chain.get_balance(public_key),
            }
        )

    @app.route("/block", methods=["GET"])
    def get_chain():
        chain_data = node_chain.chain_to_list()
        return jsonify({"length": len(chain_data), "chain": chain_data})

    @app.route("/mempool", methods=["GET"])
    def get_mempool():
        return jsonify({"mempool": node_chain.pending_transactions})

    @app.route("/transaction", methods=["POST"])
    def execute_transaction():
        incoming_data = request.get_json(silent=True) or {}
        receiver = incoming_data.get("receiver")
        amount = incoming_data.get("amount")

        if receiver is None or amount is None:
            return jsonify({"error": "Missing receiver or amount parameters."}), 400

        try:
            new_tx = Transaction(
                sender=identity.get_public_key_pem(),
                receiver=receiver,
                amount=amount,
            )
        except (TypeError, ValueError):
            return jsonify({"error": "Amount must be numeric."}), 400

        new_tx.sign_transaction(identity.private_key)
        added, message = node_chain.add_pending_transaction(new_tx)
        if not added:
            return jsonify({"error": message}), 400

        for node in node_chain.nodes:
            try:
                http_post_json(
                    f"{node}/receive_transaction",
                    new_tx.to_dict(),
                    timeout=3,
                )
            except (urllib_error.URLError, json.JSONDecodeError):
                continue

        return (
            jsonify(
                {
                    "message": "Transaction signed and added to the mempool.",
                    "signature": new_tx.signature,
                    "transaction_hash": new_tx.transaction_hash,
                }
            ),
            201,
        )

    @app.route("/receive_transaction", methods=["POST"])
    def receive_transaction():
        incoming_data = request.get_json(silent=True) or {}

        try:
            tx = Transaction.from_dict(incoming_data)
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Malformed transaction payload."}), 400

        added, message = node_chain.add_pending_transaction(tx)
        if not added:
            return jsonify({"error": message}), 400

        return jsonify({"message": message}), 201

    @app.route("/validate", methods=["POST"])
    def validate_transaction():
        incoming_data = request.get_json(silent=True) or {}

        try:
            tx = Transaction.from_dict(incoming_data)
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Malformed transaction payload."}), 400

        if tx.verify_transaction():
            return jsonify({"message": "Signature is valid."}), 200
        return jsonify({"error": "Signature is invalid."}), 400

    @app.route("/mine", methods=["GET"])
    def mine_mempool():
        new_block = node_chain.mine_pending_transactions(identity.get_public_key_pem())
        if new_block is None:
            return jsonify({"message": "No transactions in the mempool to mine."}), 400

        return (
            jsonify(
                {
                    "message": "Block successfully mined and appended to the chain.",
                    "block_hash": new_block.hash,
                    "reward": MINING_REWARD,
                }
            ),
            200,
        )

    @app.route("/register", methods=["POST"])
    def register_nodes():
        incoming_data = request.get_json(silent=True) or {}
        nodes = incoming_data.get("nodes")

        if not isinstance(nodes, list):
            return jsonify({"error": "Please supply a valid list of nodes."}), 400

        added_nodes = node_chain.add_nodes(nodes)
        return (
            jsonify(
                {
                    "message": "Nodes successfully registered to the network.",
                    "total_nodes": list(node_chain.nodes),
                    "added_nodes": added_nodes,
                }
            ),
            201,
        )

    @app.route("/nodes", methods=["GET"])
    def get_registered_nodes():
        return jsonify({"total_nodes": list(node_chain.nodes)}), 200

    @app.route("/sync", methods=["GET"])
    def consensus():
        current_max_length = len(node_chain.chain)
        best_chain = None

        for node in node_chain.nodes:
            try:
                status_code, response_data = http_get_json(f"{node}/block", timeout=3)
            except (urllib_error.URLError, json.JSONDecodeError):
                continue

            if status_code != 200:
                continue

            chain_data = response_data.get("chain", [])
            chain_length = response_data.get("length", 0)

            if chain_length > current_max_length and node_chain.is_valid_chain_data(chain_data):
                current_max_length = chain_length
                best_chain = chain_data

        if best_chain and node_chain.replace_chain(best_chain):
            return (
                jsonify(
                    {
                        "message": "Local chain replaced with the longest valid network chain.",
                        "new_chain": best_chain,
                    }
                ),
                200,
            )

        return jsonify({"message": "Local chain is already the longest valid chain."}), 200

    return app
