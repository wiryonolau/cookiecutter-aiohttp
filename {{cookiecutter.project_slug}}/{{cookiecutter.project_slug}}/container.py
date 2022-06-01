from dependency_injector import containers, providers

from {{ cookiecutter.project_slug }} import daemon, db, provider, service, repository
from {{ cookiecutter.project_slug }}.http import action as http_action
from {{ cookiecutter.project_slug }}.http import app as http_app
from {{ cookiecutter.project_slug }}.http import middleware as http_middleware
from {{ cookiecutter.project_slug }}.http import view_helper as http_view_helper

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.ThreadSafeSingleton(
        db.Database,
        data_path=config.data_path
    )

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
            providers.ThreadSafeSingleton(
                http_middleware.BasicAuthMiddleware,
                auth=config.http.auth
            ),
            providers.ThreadSafeSingleton(http_middleware.SessionMiddleware),
            providers.ThreadSafeSingleton(http_middleware.ErrorMiddleware),
        ),
        http_routes=providers.List(
            providers.ThreadSafeSingleton(
                http_action.HomeAction
            )
        ),
        debug=config.debug
    )

    http_server = providers.ThreadSafeSingleton(
        daemon.HttpServer,
        application=http_application,
        host=config.http.host,
        port=config.http.port,
        cert=config.http.cert,
        key=config.http.key
    )

    daemon_service = providers.ThreadSafeSingleton(
        service.DaemonService,
        daemons=providers.List(
            http_server,
        ),
        async_init=providers.List()
    )

    dev_daemon_service = providers.ThreadSafeSingleton(
        service.DaemonService,
        daemons=providers.List(),
        async_init=providers.List()
    )
