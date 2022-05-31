import aiohttp_debugtoolbar
import aiohttp_jinja2
import os
import weakref

from aiohttp import web
from {{ cookiecutter.project_slug }}.util import get_logger
from jinja2 import DebugUndefined, Environment, FileSystemLoader
from pathlib import Path

class HttpApplication:
    def __init__(
        self,
        http_middleware=[],
        http_routes=[],
        debug=False
    ):
        self._http_middleware = http_middleware
        self._http_routes = http_routes
        self._debug = debug

        self._app: web.Application

        self._logger = get_logger(self.__class__.__name__)
        self._app_dir = Path(__file__).parent.absolute()

    def __call__(self):
        self._app = web.Application(
            middlewares=[m.middleware() for m in self._http_middleware]
        )

        # Websocket client records
        self._app['websockets'] = weakref.WeakSet()

        if self._debug:
            aiohttp_debugtoolbar.setup(self._app, intercept_redirects=False)

        self._register_view()
        self._register_asset()
        self._register_route()

        return self._app

    def _register_view(self):
        aiohttp_jinja2.setup(
            self._app,
            loader=FileSystemLoader(
                os.path.join(self._app_dir, "view")
            ),
            undefined=DebugUndefined,
            enable_async=True
        )

    def _register_asset(self):
        self._app.router.add_static('/css',
                                    os.path.join(
                                        self._app_dir, "asset", "css"),
                                    follow_symlinks=True)
        self._app.router.add_static('/js',
                                    os.path.join(
                                        self._app_dir, "asset", "js", "dist"),
                                    follow_symlinks=True)
        self._app.router.add_static('/img',
                                    os.path.join(
                                        self._app_dir, "asset", "img"),
                                    follow_symlinks=True)
        self._app.router.add_static('/lib',
                                    os.path.join(
                                        self._app_dir, "node_modules"),
                                    follow_symlinks=True)

    def _register_route(self):
        for route in self._http_routes:
            if hasattr(route, "name"):
                name = route.name
            else:
                name = None

            # Allow registration of single path or list of path
            paths = route.path if isinstance(route.path, list) else [route.path]

            for path in paths:
                if hasattr(route, "get"):
                    self._app.router.add_get(path, route.get, name=name)

                if hasattr(route, "ws"):
                    self._app.router.add_get("/ws" + path, route.ws, name=name)

                if hasattr(route, "post"):
                    self._app.router.add_post(path, route.post, name=name)

                if hasattr(route, "head"):
                    self._app.router.add_head(path, route.head, name=name)

                if hasattr(route, "put"):
                    self._app.router.add_put(path, route.put, name=name)

                if hasattr(route, "patch"):
                    self._app.router.add_patch(path, route.patch, name=name)

                if hasattr(route, "delete"):
                    self._app.router.add_delete(path, route.delete, name=name)
