import asyncio
import json
import sys
import os
import traceback
import aiohttp_jinja2
from aiohttp import WSMsgType, web
from {{ cookiecutter.project_slug }}.util import get_logger, Map

class Response(web.Response):
    def __init__(
        self,
        template,
        request,
        context = {},
        css = [],
        js = [],
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._css: list = []
        self._js: list = []

        self._template = template
        self._request = request
        self._context = context

        self._logger = get_logger(self.__class__.__name__)

        for stylesheet in css:
            self.add_css(**stylesheet)

        for script in js:
            self.add_js(**script)

    @property
    def css(self):
        return self._css

    @property
    def js(self):
        return self._js

    def add_css(self, path: str, attrs: dict = {}):
        attrs_string = ["{}=\"{}\"".format(k, v) for k, v in attrs.items()]
        self._css.append(
            "<link rel=\"stylesheet\" href=\"{}\" {} />".format(
                path, " ".join(attrs_string))
        )

    def add_js(self, path: str, type: str = "text/javascript", attrs: dict = {}) -> None:
        attrs_string = ["{}=\"{}\"".format(k, v) for k, v in attrs.items()]
        self._js.append(
            "<script type=\"{}\" src=\"{}\" {}></script>".format(
                type, path, " ".join(attrs_string))
        )

    def get_layout_context(self):
        return {
            "layout": self._context.get("layout", {})
        }

    # Helper is injected from layout
    async def render(self, helper = {}):
        self._context["helper"] = helper

        return await aiohttp_jinja2.render_string_async(
            self._template,
            self._request,
            self._context
        )

class JsonResponse(web.Response):
    def __init__(
        self,
        reques,
        context = {},
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._request = request
        self._context = context

        self._logger = get_logger(self.__class__.__name__)

    async def render(self, helper = {}):
        return await aiohttp_jinja2.render_string_async(
            "/layout/json.j2",
            self._request,
            {
                "content" : self._context
            }
        )

class PdfResponse(web.Response):
    def __init__(
        self,
        request,
        context,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._request = request
        self._context = context

        self._logger = get_logger(self.__class__.__name__)

    async def render(self, helper = {}):
        return self._context

class WebSocketResponse(web.WebSocketResponse):
    def __init__(
        self,
        request,
        on_text = None,
        on_binary = None,
        on_ping = None,
        on_pong = None,
        on_close = None
    ):
        self._ws : web.WebSocketResponse = web.WebSocketResponse()
        self._on_text = on_text
        self._on_binary = on_binary
        self._on_ping = on_ping
        self._on_pong = on_pong
        self._on_close = on_close
        self._request = request

        self._helper = Map({
            "broadcast" : self._broadcast
        })

        self._logger = get_logger(self.__class__.__name__)

    async def __call__(self) -> web.WebSocketResponse:
        await self._ws.prepare(self._request)
        await self._register()

        self._logger.debug("connect ws")

        try:
            async for msg in self._ws:
                if msg.type == WSMsgType.TEXT:
                    if self._on_text is not None:
                        await self._on_text(self._ws, msg, helper=self._helper, new=True)
                elif msg.type == WSMsgType.BINARY:
                    if self._on_binary is not None:
                        await self._on_binary(self._ws, msg, helper=self._helper, new=True)
                elif msg.type == WSMsgType.PING:
                    if self._on_ping is not None:
                        await self._on_ping(msg)
                    await self._ws.ping()
                elif msg.type == WSMsgType.PONG:
                    if self._on_pong is not None:
                        await self._on_pong(msg)
                    await self._ws.pong()
                elif self._ws.closed:
                    code = int(self._ws.close_code) if self._ws.close_code else 0
                    if self._on_close is not None:
                        await self._on_close(self._ws)
                    await self._ws.close(
                        code=code,
                        message=msg.extra)
        except:
            self._logger.debug(sys.exc_info())

        return self._ws

    async def _broadcast(self, message):
        await asyncio.wait([c.send_str(message) for c in self._request.app['websockets']])

    async def _register(self):
        self._request.app['websockets'].add(self._ws)
