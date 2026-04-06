"""Catch-all Vercel Python entrypoint for `/api/*` routes."""

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

        if path in {"/health", "/docs", "/redoc", "/openapi.json"}:
            normalized_scope["path"] = path
        elif path.startswith("/api"):
            normalized_scope["path"] = path
        else:
            normalized_scope["path"] = f"/api{path if path.startswith('/') else '/' + path}"

        await self.app(normalized_scope, receive, send)


app = PathNormalizedASGIApp(backend_app)
