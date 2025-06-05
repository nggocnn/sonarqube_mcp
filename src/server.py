import os
import asyncio
from mcp.server.fastmcp import FastMCP
from sonarqube.client import SonarQubeClient

mcp = FastMCP(name="SonarQube MCP Server")

SONARQUBE_URL = os.environ.get("SONARQUBE_URL", "http://localhost:9000")
SONARQUBE_TOKEN = os.environ.get("SONARQUBE_TOKEN", "")
SONARQUBE_ORGANIZATION = os.environ.get("SONARQUBE_ORGANIZATION", None)

async def init_sonar_client() -> SonarQubeClient:
  """Initialize the SonarQube client asynchronously."""
  try:
    client = await SonarQubeClient.create(
      base_url=SONARQUBE_URL,
      token=SONARQUBE_TOKEN,
      organization=SONARQUBE_ORGANIZATION,
    )
    return client
  except Exception as e:
    raise ConnectionError(f"Failed to initialize SonarQube client: {str(e)}")

loop = asyncio.get_event_loop()
sonar_client = loop.run_until_complete(init_sonar_client())
