import requests
import argparse
import json
from wallet import Wallet

wallet = Wallet()

def register(port, node):
    requests.post(f"http://127.0.0.1:{port}/register", json={'node': node})


def send(port, receiver, amount):
    sender = wallet.get_public_key()

    data = json.dumps({
        'sender': sender,
        'receiver': receiver,
        'amount': amount
    })

    signature = wallet.sign(data).hex()

    tx = {
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'signature': signature
    }

    res = requests.post(f"http://127.0.0.1:{port}/transaction", json=tx)
    print(res.json())


def mine(port):
    res = requests.get(f"http://127.0.0.1:{port}/mine")
    print(res.json())


def mempool(port):
    res = requests.get(f"http://127.0.0.1:{port}/mempool")
    print(res.json())


def profile(port):
    res = requests.get(f"http://127.0.0.1:{port}/profile")
    print(res.json())


def chain(port):
    res = requests.get(f"http://127.0.0.1:{port}/chain")
    print(res.json())


def sync(port):
    res = requests.get(f"http://127.0.0.1:{port}/sync")
    print(res.json())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('--node')
    parser.add_argument('--receiver')
    parser.add_argument('--amount', type=int)

    args = parser.parse_args()

    if args.command == 'register':
        register(args.port, args.node)
    elif args.command == 'send':
        send(args.port, args.receiver, args.amount)
    elif args.command == 'mine':
        mine(args.port)
    elif args.command == 'mempool':
        mempool(args.port)
    elif args.command == 'profile':
        profile(args.port)
    elif args.command == 'chain':
        chain(args.port)
    elif args.command == 'sync':
        sync(args.port)