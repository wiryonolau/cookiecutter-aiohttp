import ssl
import sys

from aiohttp import web
from {{ cookiecutter.project_slug }}.abc import AbstractAsyncioFuture
from {{ cookiecutter.project_slug }}.http.app import HttpApplication

class HttpServer(AbstractAsyncioFuture):
    def _init(
        self,
        application,
        host="0.0.0.0",
        port=8080,
        cert=None,
        key=None
    ):
        self._application = application
        self._host = host
        self._port = port
        self._cert = cert
        self._key = key

        self._runner = web.AppRunner(self._application())

        self._add_task(self._start_server)

    async def _pre_shutdown(self, timeout: int = 5) -> None:
        self._logger.info("Shutting down HTTP Server")
        try:
            await self._runner.cleanup()
        except:
            self._logger.debug(sys.exc_info())

    async def _start_server(self) -> None:
        self._logger.info("Starting HTTP Server")

        ssl_context = None
        if ((self._cert and self._key) is not None):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(self._cert, self._key)
            ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        try:
            await self._runner.setup()

            site = web.TCPSite(self._runner,
                               self._host,
                               self._port,
                               ssl_context=ssl_context
                               )

            await site.start()
        except:
            self._logger.debug(sys.exc_info())
