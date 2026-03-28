"""Conflict-proof hosted entrypoint for FastMCP deployments.

Some hosting platforms may resolve `mcp/server.py:mcp` using module imports,
which can clash with the third-party `mcp` package name. This file loads the
local server file explicitly by path and exposes `mcp` for the host runtime.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

_SERVER_FILE = Path(__file__).resolve().parent / "mcp" / "server.py"
_SPEC = importlib.util.spec_from_file_location("email_bridge_server", _SERVER_FILE)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Unable to load server module from {_SERVER_FILE}")

_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

# Exported symbol for hosted entrypoint, e.g. host_entrypoint.py:mcp
mcp = _MODULE.mcp

# ASGI app export for hosts that expect an application object (main.py:app style).
_transport = os.getenv("MCP_TRANSPORT", "streamable-http")
_path = os.getenv("MCP_PATH", "/mcp")
app = mcp.http_app(transport=_transport, path=_path)


def main() -> None:
    """Optional callable entrypoint for platforms that invoke a function."""
    _MODULE.main()
