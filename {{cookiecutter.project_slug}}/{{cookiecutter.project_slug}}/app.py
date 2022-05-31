import logging
import argparse
import sys
import os
from {{ cookiecutter.project_slug }} import  __version__
from {{ cookiecutter.project_slug }}.container import Container
from {{ cookiecutter.project_slug }}.util import get_logger

from pprint import pprint

# This is app to adev runserver livereload
# TcpServer is run from aiohttp devtools
def app(as_dev=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("-k",
                        "--key",
                        help="Server Private Key",
                        default=os.getenv("PRIVATEKEY", ''))
    parser.add_argument("-c",
                        "--cert",
                        help="Server Certificate",
                        default=os.getenv("CERTIFICATE", ''))
    parser.add_argument("--host",
                        help="HTTP listen address",
                        default=os.getenv("HTTPHOST", "0.0.0.0"))
    parser.add_argument("--port",
                        help="HTTP listen port",
                        default=os.getenv("HTTPPORT", 8080))
    parser.add_argument("--debug", help="Debug",
                        action="store_true",
                        default=bool(os.getenv("DEBUG", False)))
    parser.add_argument("--version" , help="Print version", action="store_true", default=False)
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit()

    default_logging_level = logging.DEBUG if args.debug is True else logging.INFO
    if as_dev is True:
        default_logging_level = logging.DEBUG

    logging.basicConfig(
        level = default_logging_level,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
        handlers = [
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Disable logging for other library
    for key in logging.Logger.manager.loggerDict:
        logging_level = logging.CRITICAL
        if key in ["{{ cookiecutter.project_slug }}", "aiohttp.access"]:
            logging_level = default_logging_level
        logging.getLogger(key).setLevel(logging_level)

    data_path = args.data or os.path.join(os.path.expanduser("~"), ".config", "{{ cookiecutter.project_slug }}")
    os.makedirs(data_path, exist_ok=True)

    container = Container()
    container.init_resources()
    container.config.from_dict({
        "data_path" : data_path,
        "http" : {
            "host" : str(args.host),
            "port" : int(args.port),
            "cert" : str(args.cert),
            "key" : str(args.key)
        },
        "debug" : True if as_dev else args.debug,
        "as_dev" : as_dev,
        "version" : __version__
    })

    container.wire(modules=[sys.modules[__name__]])
    container.db().init()

    if as_dev:
        container.dev_daemon_service().start(True)
        http_app = container.http_application()
        return http_app()
    else:
        container.daemon_service().start()
        container.daemon_service().shutdown()
