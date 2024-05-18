from fastapi import FastAPI
from .http_exceptions import global_exception_handler

def register_exception_handlers(app: FastAPI):
    app.exception_handler(Exception)(global_exception_handler)
