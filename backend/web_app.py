from flask import request, Flask, Response


class WebApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def create_web_app() -> WebApp:
    web_app = WebApp(import_name=__name__)

    @web_app.route('/', methods=['GET'])
    def transactions():
        return Response('ahoj', status=200)

    return web_app
