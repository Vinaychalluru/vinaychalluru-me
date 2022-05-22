import logging

import azure.functions as func

from portfolio.wsgi import application


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    try:
        return func.WsgiMiddleware(application).handle(req, context)
    except Exception as ex:
        logging.error(ex.args[0], exc_info=True)
