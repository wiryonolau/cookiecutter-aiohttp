from {{ cookiecutter.project_slug }}.abc import AbstractHttpAction
from {{ cookiecutter.project_slug }}.http.web import Response

class HomeAction(AbstractHttpAction):
    path = "/"

    async def get(self, request):
        return Response(
            template="/home/index.j2",
            request=request,
            context={
                "layout": {
                    "page_title": "Home"
                },
                "text": "Hello World"
            }
        )
