import ssl
import sys

from aiohttp import web
from {{ cookiecutter.project_slug }}.abc import AbstractAsyncioFuture
from {{ cookiecutter.project_slug }}.http.app import HttpApplication

class HttpServer(AbstractAsyncioFuture):
    def _init(
        self,
        application: HttpApplication,
        host: str = "0.0.0.0",
        port: int = 8080
    ):
        self._application = application
        self._host = host
        self._port = port

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
