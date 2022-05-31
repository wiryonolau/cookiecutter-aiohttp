from dependency_injector import containers, providers

from {{ cookiecutter.project_slug }} import daemon, db, provider, service, repository
from {{ cookiecutter.project_slug }}.http import action as http_action
from {{ cookiecutter.project_slug }}.http import app as http_app
from {{ cookiecutter.project_slug }}.http import middleware as http_middleware
from {{ cookiecutter.project_slug }}.http import view_helper as http_view_helper

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    http_view_helper = providers.Dict({})

    http_application = providers.ThreadSafeSingleton(
        http_app.HttpApplication,
        http_middleware=providers.List(
            providers.ThreadSafeSingleton(
                http_middleware.LayoutMiddleware,
                view_helper=http_view_helper,
                as_dev=config.as_dev,
                version=config.version
            ),
            providers.ThreadSafeSingleton(http_middleware.SessionMiddleware),
            providers.ThreadSafeSingleton(http_middleware.ErrorMiddleware)
        ),
        http_routes=providers.List(
            providers.ThreadSafeSingleton(
                http_action.HomeAction
            )
        ),
        debug=config.debug
    )

    http_server = providers.ThreadSafeSingleton(
        daemon.HttpServer, http_application
    )

    daemon_service = providers.ThreadSafeSingleton(
        service.DaemonService,
        daemons=providers.List(
            http_server,
        )
    )

    dev_daemon_service = providers.ThreadSafeSingleton(
        service.DaemonService,
        daemons=providers.List()
    )