import logging
import os
import sys
import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from main import app

# Adjust PYTHONPATH for FastAPI Application
sys.path.append(os.getcwd())
logging.info(f"sys.path : {sys.path}")

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    try:
        return await func.AsgiMiddleware(app).handle(req, context)
    except Exception as ex:
        logging.error(ex.args[0], exc_info=True)
        return func.HttpResponse(
            str(ex),
            status_code=500
        )
