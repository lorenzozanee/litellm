import re
from collections.abc import Iterable, Mapping
from typing import Final, TypeAlias

ToolParam: TypeAlias = Mapping[str, object]

LITELLM_PROXY_MCP_SERVER_URL: Final = "litellm_proxy"
LITELLM_PROXY_MCP_SERVER_URL_PREFIX: Final = f"{LITELLM_PROXY_MCP_SERVER_URL}/mcp/"
_PROXY_MCP_PATH_RE: Final = re.compile(r"^https?://.+/mcp/([^/]+)$")


def mcp_server_url(tool: ToolParam) -> str | None:
    if not isinstance(tool, dict) or tool.get("type") != "mcp":
        return None
    server_url: Final = tool.get("server_url")
    return server_url if isinstance(server_url, str) else None


def names_gateway_explicitly(tool: ToolParam) -> bool:
    return (mcp_server_url(tool) or "").startswith(LITELLM_PROXY_MCP_SERVER_URL)


def proxy_path_mcp_name(tool: ToolParam) -> str | None:
    server_url: Final = mcp_server_url(tool)
    match: Final = None if server_url is None else _PROXY_MCP_PATH_RE.match(server_url)
    return None if match is None else match.group(1)


def should_use_litellm_mcp_gateway(tools: Iterable[ToolParam] | None) -> bool:
    return any(
        names_gateway_explicitly(tool) or proxy_path_mcp_name(tool) is not None
        for tool in tools or ()
    )
