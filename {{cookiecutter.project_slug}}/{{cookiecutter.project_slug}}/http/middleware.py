import base64
import aiohttp_jinja2
import sys
import os
import asyncio

from {{ cookiecutter.project_slug }}.abc import AbstractMiddleware
from {{ cookiecutter.project_slug }}.util import dict_merge
from {{ cookiecutter.project_slug }}.http.web import Response, JsonResponse, PdfResponse
from aiohttp_basicauth_middleware import basic_auth_middleware
from cryptography import fernet
from aiohttp import web
from aiohttp_session import get_session, session_middleware, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp.web_middlewares import _Middleware

class BasicAuthMiddleware(AbstractMiddleware):
    def __init__(self):
        pass

    def middleware(self):
        return basic_auth_middleware(('/',) , {'admin' : '888888'})

class SessionMiddleware(AbstractMiddleware):
    def __init__(self):
        super().__init__()
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        self._cookie_storage = EncryptedCookieStorage(
            secret_key,
            max_age=900
        )

    def middleware(self):
        return session_middleware(self._cookie_storage)

class NavigationMiddleware(AbstractMiddleware):
    def __init__(self):
        super().__init__()

class ErrorMiddleware(AbstractMiddleware):
    def middleware(self):
        return self._factory

    @web.middleware
    async def _factory(
        self,
        request,
        handler
    ):
        error: list = []

        try:
            return await handler(request)
        except web.HTTPRedirection:
            raise
        except web.HTTPError as we:
            error.append(str(we))
        except asyncio.CancelledError as ce:
            error.append(str(ce))
        except Exception as ex:
            error.append(str(ex))

        return Response(
            template="/layout/error.j2",
            request=request,
            context={
                "layout" : {
                    "title" : "{{ cookiecutter.project_name }}",
                    "breadcrumbs": [
                        {
                            "label": "home",
                            "url": "/"
                        },
                        {
                            "label": "error"
                        }
                    ],
                    "page_title": "System Error"
                },
                "error" : error
            }
        )


class LayoutMiddleware(AbstractMiddleware):
    def __init__(self, view_helper={}, as_dev=False, version=None):
        super().__init__()
        self._view_helper = view_helper
        self._as_dev = as_dev
        self._version = version

    def middleware(self):
        return self._factory

    @web.middleware
    async def _factory(
        self,
        request,
        handler,
    ):
        response = await handler(request)
        session = await get_session(request)

        try:
            # must use getattr to retrieve custom attribute since handler always return web.StreamResponse type
            if hasattr(response, "render"):
                render = getattr(response, "render")
                content = await render(self._view_helper)
            elif hasattr(response, "text"):
                content = getattr(response, "text")
            else:
                return response

            if isinstance(response, JsonResponse):
                return web.Response(body=content, content_type="application/json")
            elif isinstance(response, PdfResponse):
                return web.Response(body=content, content_type="application/pdf", headers={
                    "Content-Disposition" : "inline;filename=downloaded.pdf"
                })

            layout = '/layout/default.j2'
            context = {
                "layout" : {
                    "title" : "{{ cookiecutter.project_slug }}",
                    "as_dev" : self._as_dev,
                    "version" : self._version
                },
                "helper" : self._view_helper,
                "script" : {
                    "css" :  getattr(response, "css") if hasattr(response, "css") else [],
                    "js" : getattr(response, "js") if hasattr(response, "js") else []
                },
                "content" : content
            }

            if hasattr(response, "get_layout_context"):
                get_layout_context = getattr(response, "get_layout_context")
                context = dict_merge(context, get_layout_context())

            return await aiohttp_jinja2.render_template_async(
                layout,
                request,
                context
            )
        except:
            self._logger.debug(sys.exc_info())
            return web.HTTPNotFound()
