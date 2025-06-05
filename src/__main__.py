import argparse
from server import mcp
from tools import *


def main():
    parser = argparse.ArgumentParser(description="Run MCP with specified transport")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport method for MCP (default: stdio)",
    )

    args = parser.parse_args()

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
