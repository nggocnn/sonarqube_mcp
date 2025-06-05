import os
from tools import *

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

def main():
  mcp.run(transport=MCP_TRANSPORT)

if __name__ == "__main__":
  main()