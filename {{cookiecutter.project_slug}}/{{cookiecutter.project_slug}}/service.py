import asyncio
import os
import sys

from {{ cookiecutter.project_slug }}.abc import AbstractService

class DaemonService(AbstractService):
    def _init(self, daemons, async_init):
        self._daemons = daemons
        self._async_init = async_init

    @property
    def daemons(self):
        return self._daemons

    def start(self, as_dev=False):
        self._logger.info("Start Daemon")
        if as_dev is True:
            try:
                for i in self._async_init:
                    asyncio.ensure_future(i.async_init())

                for d in self._daemons:
                    d.start()
            except asyncio.CancelledError:
                self._logger.info("Receive CancelledError")
            except KeyboardInterrupt:
                self._logger.info("Receive Keyboard Interrupt")
            except:
                self._logger.info(sys.exc_info())
            # Shutdown is handle by aiohttp devtools
        else:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                for i in self._async_init:
                    asyncio.ensure_future(i.async_init())

                for d in self._daemons:
                    d.start()
                loop.run_forever()
            except asyncio.CancelledError:
                self._logger.info("Receive CancelledError")
            except KeyboardInterrupt:
                self._logger.info("Receive Keyboard Interrupt")
            except:
                self._logger.info(sys.exc_info())
            self.shutdown()

    def shutdown(self):
        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(asyncio.wait(
                [d.shutdown() for d in self._daemons]))
            loop.close()
        except:
            self._logger.debug(sys.exc_info())
