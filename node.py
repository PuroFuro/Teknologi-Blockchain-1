from flask import Flask, request, jsonify
from blockchain import Blockchain
from wallet import Wallet
from utils import verify_signature
import requests
import argparse
import json

app = Flask(__name__)

# Inisialisasi
blockchain = Blockchain()
wallet = Wallet()
nodes = set()


# =========================
# REGISTER NODE
# =========================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    node = data.get('node')

    if not node:
        return jsonify({'error': 'Invalid node'}), 400

    nodes.add(node)
    return jsonify({'message': 'Node registered', 'nodes': list(nodes)}), 201


# =========================
# LIHAT NODE TERHUBUNG
# =========================
@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(list(nodes)), 200


# =========================
# TRANSACTION + SIGNATURE VALIDATION
# =========================
@app.route('/transaction', methods=['POST'])
def transaction():
    tx = request.get_json()

    sender = tx.get('sender')
    receiver = tx.get('receiver')
    amount = tx.get('amount')
    signature = tx.get('signature')

    # Validasi format
    if not sender or not receiver or not amount:
        return jsonify({'error': 'Invalid transaction format'}), 400

    # Data yang ditandatangani
    data = json.dumps({
        'sender': sender,
        'receiver': receiver,
        'amount': amount
    })

    # Verifikasi signature (kecuali SYSTEM)
    if sender != "SYSTEM":
        if not signature:
            return jsonify({'error': 'Missing signature'}), 400

        if not verify_signature(sender, data, bytes.fromhex(signature)):
            return jsonify({'error': 'Invalid signature'}), 400

    # Tambahkan ke mempool
    blockchain.add_transaction(tx)

    # Broadcast ke node lain
    for node in nodes:
        try:
            requests.post(f"{node}/transaction", json=tx)
        except:
            pass

    return jsonify({'message': 'Transaction added'}), 201


# =========================
# MINING (REWARD)
# =========================
@app.route('/mine', methods=['GET'])
def mine():
    reward_tx = {
        'sender': 'SYSTEM',
        'receiver': wallet.get_public_key(),
        'amount': 67,
        'signature': ''
    }

    blockchain.add_transaction(reward_tx)

    prev_hash = blockchain.hash(blockchain.last_block())
    block = blockchain.create_block(prev_hash)

    return jsonify(block), 200


# =========================
# GET CHAIN
# =========================
@app.route('/chain', methods=['GET'])
def chain():
    return jsonify(blockchain.chain), 200


# =========================
# GET MEMPOOL
# =========================
@app.route('/mempool', methods=['GET'])
def mempool():
    return jsonify(blockchain.mempool), 200


# =========================
# PROFILE (BALANCE + PUBLIC KEY)
# =========================
@app.route('/profile', methods=['GET'])
def profile():
    balance = 3
    my_key = wallet.get_public_key()

    for block in blockchain.chain:
        for tx in block['transactions']:
            if tx['receiver'] == my_key:
                balance += tx['amount']
            if tx['sender'] == my_key:
                balance -= tx['amount']

    return jsonify({
        'public_key': my_key,
        'balance': balance
    }), 200


# =========================
# SYNC CHAIN (LONGEST CHAIN)
# =========================
@app.route('/sync', methods=['GET'])
def sync():
    global blockchain

    longest_chain = blockchain.chain

    for node in nodes:
        try:
            res = requests.get(f"{node}/chain")
            chain = res.json()

            if len(chain) > len(longest_chain):
                longest_chain = chain
        except:
            pass

    blockchain.chain = longest_chain
    return jsonify({'message': 'Synced'}), 200


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name')
    parser.add_argument('-p', '--port', type=int)
    args = parser.parse_args()

    print(f"Starting node {args.name} on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port)