import argparse
import json
from urllib import error as urllib_error
from urllib import request as urllib_request

def get_url(port):
    return f"http://127.0.0.1:{port}"


def make_request(method, url, payload=None):
    request_data = None
    headers = {}

    if payload is not None:
        request_data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    outgoing_request = urllib_request.Request(
        url,
        data=request_data,
        headers=headers,
        method=method,
    )

    try:
        with urllib_request.urlopen(outgoing_request) as response:
            response_body = response.read().decode("utf-8")
            return response.status, response_body
    except urllib_error.HTTPError as error:
        return error.code, error.read().decode("utf-8")

def print_response(response_body):
    try:
        print(json.dumps(json.loads(response_body), indent=2))
    except json.JSONDecodeError:
        print(response_body)

def main():
    parser = argparse.ArgumentParser(description="Blockchain CLI Client")
    parser.add_argument('command', choices=['profile', 'chain', 'register', 'send', 'mempool', 'mine', 'sync'], 
                        help='The action you want to perform')
    parser.add_argument('-p', '--port', type=int, default=5000, 
                        help='Port of the node you are talking to (default: 5000)')
    
    # Optional arguments for specific commands
    parser.add_argument('--node', type=str, help='Target node URL (used with "register")')
    parser.add_argument('--receiver', type=str, help='Receiver public key (used with "send")')
    parser.add_argument('--amount', type=float, help='Amount to send (used with "send")')

    args = parser.parse_args()
    base_url = get_url(args.port)

    try:
        if args.command == 'profile':
            _, response_body = make_request("GET", f"{base_url}/profile")
            print_response(response_body)
            
        elif args.command == 'chain':
            _, response_body = make_request("GET", f"{base_url}/block")
            print_response(response_body)

        elif args.command == 'register':
            if not args.node:
                print("❌ Error: Please provide --node URL (e.g., --node http://127.0.0.1:5001)")
                return
            _, response_body = make_request(
                "POST",
                f"{base_url}/register",
                {"nodes": [args.node]},
            )
            print_response(response_body)

        elif args.command == 'send':
            if args.receiver is None or args.amount is None:
                print("❌ Error: Please provide --receiver and --amount")
                return
            # We handle the newline characters in the pasted PEM key
            receiver_key = args.receiver.replace('\\n', '\n')
            _, response_body = make_request(
                "POST",
                f"{base_url}/transaction",
                {"receiver": receiver_key, "amount": args.amount},
            )
            print_response(response_body)

        elif args.command == 'mempool':
            _, response_body = make_request("GET", f"{base_url}/mempool")
            print_response(response_body)

        elif args.command == 'mine':
            _, response_body = make_request("GET", f"{base_url}/mine")
            print_response(response_body)

        elif args.command == 'sync':
            _, response_body = make_request("GET", f"{base_url}/sync")
            print_response(response_body)

    except urllib_error.URLError:
        print(f"❌ Error: Could not connect to node on port {args.port}. Is it running?")

if __name__ == "__main__":
    main()
