import os
from server import mcp
from tools import *

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT")


def main():
    # if MCP_TRANSPORT:
    #     mcp.run(transport=MCP_TRANSPORT)
    # else:
        mcp.run()


if __name__ == "__main__":
    main()
