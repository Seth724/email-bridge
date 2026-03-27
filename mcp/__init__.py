"""Email Bridge MCP package.

Keep this module lightweight to avoid circular imports during server discovery.
"""

__all__ = ["get_mcp"]


def get_mcp():
	"""Lazily return the FastMCP server instance."""
	from .server import mcp

	return mcp
