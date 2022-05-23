import logging
import os
import sys

import azure.functions as func

from portfolio.wsgi import application

# Adjust PYTHONPATH for Django Application Folder
sys.path.append(os.getcwd())
logging.info(f"sys.path : {sys.path}")


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    try:
        return func.WsgiMiddleware(application).handle(req, context)
    except Exception as ex:
        logging.error(ex.args[0], exc_info=True)
