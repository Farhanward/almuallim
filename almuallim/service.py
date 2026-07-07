"""Almuallim teaching engine as a local HTTP service.

``POST /api/teach`` accepts ``{"code": "..."}`` (Python source) or
``{"path": "..."}`` (local file) and returns an Arabic breakdown lesson with a
quiz. Code is analyzed via AST in-memory — nothing is executed.
"""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .analyzer import teach_python, teach_python_source
from .http_base import BaseServiceHandler, build_server


def _teach_route(data: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    code = str(data.get("code") or "")
    raw_path = str(data.get("path") or "").strip()
    if not code.strip() and not raw_path:
        return 400, {"ok": False, "error": "missing 'code' or 'path'"}
    try:
        if code.strip():
            lesson = teach_python_source(code, display_path=str(data.get("name") or "uploaded.py"))
        else:
            target = Path(raw_path)
            if not target.exists():
                return 404, {"ok": False, "error": f"path not found: {target}"}
            lesson = teach_python(target)
    except SyntaxError as exc:
        return 422, {"ok": False, "error": f"invalid python source: {exc}"}
    return 200, {"ok": True, **lesson}


class Handler(BaseServiceHandler):
    post_routes = {"/api/teach": staticmethod(_teach_route)}


def create_server(host: str | None = None, port: int | None = None) -> ThreadingHTTPServer:
    return build_server(Handler, host=host, port=port)


def run_server(host: str | None = None, port: int | None = None) -> None:
    from .version import __version__

    server = create_server(host=host, port=port)
    print(f"almuallim service v{__version__}: http://{server.server_address[0]}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
