"""Vercel Python entrypoint for MedRoundTable."""

from urllib.parse import parse_qs

from backend.main import app as backend_app


class PathNormalizedASGIApp:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or "/"
        normalized_scope = dict(scope)
        query_string = scope.get("query_string", b"").decode()
        rewritten_path = parse_qs(query_string).get("__path", [None])[0]

        if rewritten_path:
            cleaned = rewritten_path.lstrip('/')
            if cleaned in {"health", "docs", "redoc", "openapi.json"}:
                normalized_scope["path"] = f"/{cleaned}"
            else:
                normalized_scope["path"] = f"/api/{cleaned}"
        elif path in {"/health", "/docs", "/redoc", "/openapi.json"}:
            normalized_scope["path"] = path
        elif path.startswith("/api"):
            normalized_scope["path"] = path
        else:
            normalized_scope["path"] = f"/api{path if path.startswith('/') else '/' + path}"

        await self.app(normalized_scope, receive, send)


app = PathNormalizedASGIApp(backend_app)
