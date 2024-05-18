import json
from src.config.database.database import get_db
from src.utils.common.record_audits import record_audit
from src.utils.common.responses.handlers.exceptions import ErrorHandler
from src.utils.common.aws.aws_ses import send_mail
from src.utils.common import constants
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session



def global_exception_handler(exc: Exception):
    status_code = 500
    message = "Internal Server Error"
    detail = "Internal Server Error"
    status = False

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
    
    return JSONResponse(status_code=status_code, content={"status_code": status_code, "message": message, "status": status})


def exception_handler(module=None, func=None, token_data=None, db=None, request=None, main_db:Session = Depends(get_db)):
    try:
        dev_details = ErrorHandler.error_for_developer(exception_url=request.url)
        error_cls = ""
        match module:
            case 'text_summarizer':
                error_cls = 'TextSummmarizerErrorMessages'
            case 'auth':
                error_cls = 'AuthErrorMessages'
            case 'common':
                error_cls = 'CommmonErrorMessages'
        
        message = eval(f"constants.{error_cls}.{func}").format(dev_details.get("exception_object"))
        print(message)
        
        record_audit(f"{func}: unhandled exception : error : {dev_details}", db=main_db, request=request)
        send_mail(dev_details=dev_details)
        return message
    
    except Exception as e:
        record_audit(f"exception_handler: unhandled exception : {e}")
        return str(e)