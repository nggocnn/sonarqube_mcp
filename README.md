SonarQube MCP Server

## Overview

The Model Context Protocol (MCP) Server for SonarQube enables AI Agent applications to efficiently manage and retrieve data from a SonarQube server.

## Example Usage

Ask your AI Agent to:

- List SonarQube projects, projects where the user has admin permissions, or projects available for scanning.
- List issues or retrieve detailed issue information.
- List available SonarQube quality gates or check the quality gate status of a project.
- Check the SonarQube server status.

## Tools

- `hotspot`: Retrieve a project's hotspots and detailed hotspot information.
- `issue`: List issues on the SonarQube server with optional filters (e.g., by project or author) or retrieve issue author details.
- `metric`: Fetch metric information and metric types.
- `permission`: Assign or revoke group/user permissions for a project or globally, and retrieve permission details.
- `project`: Create a project, list projects, or retrieve project analysis.
- `qualitygate`: Obtain quality gate information or the quality gate status of a project.
- `qualityprofile`: Retrieve or update quality profile information for a project.
- `rule`: Fetch rule information.
- `source`: Retrieve source code and issue information for solution suggestions.
- `system`: Check SonarQube server and connectivity status.

## Configuration

| Name | Description | Default Value |
| --- | --- | --- |
| `SONARQUBE_URL` | SonarQube server URL | `"http://localhost:9000"` |
| `SONARQUBE_TOKEN` | SonarQube authentication token |  |
| `SONARQUBE_ORGANIZATION` | SonarQube organization name | `None` |

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/nggocnn/sonarqube_mcp.git
cd sonarqube_mcp

# Install dependencies
pip install -r requirements.txt
# or
uv pip install .
```

## Integration

The MCP Server supports the following transport methods: `stdio`, `sse`, or `streamable-http`.

#### stdio

```json
"sonarqube_stdio": {
    "command": "python",
    "args": [
        "src/__main__.py",
        "--transport",
        "stdio"
    ],
    "env": {
        "SONARQUBE_URL": "<sonarqube_url>",
        "SONARQUBE_TOKEN": "<sonarqube_token>"
    }
}
```

#### sse

```bash
python src/__main__.py --transport sse

# or

uv run python src/__main__.py --transport sse
```

```json
"sonarqube_sse": {
    "type": "sse",
    "url": "http://127.0.0.1:8000/sse"
}
```

## Testing

You can use MCP Inspector to test and debug this MCP Server.

```bash
npx @modelcontextprotocol/inspector --config config.json --server sonarqube
```