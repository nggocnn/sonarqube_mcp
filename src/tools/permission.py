from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""

"""
)
async def add_group_permission(
    group_name: str,
    permission: str,
    project_key: Optional[str] = None,
) -> Dict[str, Any]:
    response = await sonar_client.add_group_permission(
        group_name=group_name,
        permission=permission,
        project_key=project_key,
    )
    return response


@mcp.tool(
    description="""

"""
)
async def remove_group_permission(
    group_name: str,
    permission: str,
    project_key: Optional[str] = None,
) -> Dict[str, Any]:
    response = await sonar_client.remove_group_permission(
        group_name=group_name,
        permission=permission,
        project_key=project_key,
    )
    return response


@mcp.tool(
    description="""

"""
)
async def get_group_permission(
    project_key: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    response = await sonar_client.get_group_permission(
        project_key=project_key, page=page, page_size=page_size
    )
    return response


@mcp.tool(
    description="""

"""
)
async def add_user_permission(
    username: str,
    permission: str,
    project_key: Optional[str] = None,
) -> Dict[str, Any]:
    response = await sonar_client.add_user_permission(
        username=username,
        permission=permission,
        project_key=project_key,
    )
    return response


@mcp.tool(
    description="""

"""
)
async def remove_user_permission(
    username: str,
    permission: str,
    project_key: Optional[str] = None,
) -> Dict[str, Any]:
    response = await sonar_client.remove_user_permission(
        username=username,
        permission=permission,
        project_key=project_key,
    )
    return response


@mcp.tool(
    description="""

"""
)
async def get_user_permission(
    project_key: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    response = await sonar_client.get_user_permission(
        project_key=project_key, page=page, page_size=page_size
    )
    return response
