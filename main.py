import argparse

from blockchain_node.api import create_app


def build_parser():
    parser = argparse.ArgumentParser(description="Start a Blockchain Node")
    parser.add_argument(
        "positional_name",
        type=str,
        nargs="?",
        default=None,
        help="Name of the node owner",
    )
    parser.add_argument(
        "positional_port",
        type=int,
        nargs="?",
        default=None,
        help="Port to run the server on",
    )
    parser.add_argument(
        "-n",
        "--name",
        dest="named_name",
        type=str,
        default=None,
        help="Name of the node owner",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="named_port",
        type=int,
        default=None,
        help="Port to run the server on",
    )
    return parser


def main():
    parser = build_parser()
    args, _ = parser.parse_known_args()
    node_name = args.named_name or args.positional_name or "Anonymous"
    node_port = args.named_port or args.positional_port or 5000

    app = create_app(node_name)
    print(f"[{node_name}]'s Node is booting up on port {node_port}...")
    app.run(host="127.0.0.1", port=node_port, debug=True)


if __name__ == "__main__":
    main()
