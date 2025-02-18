from fastapi.responses import JSONResponse
from src.utils.common import constants
from fastapi import status

def response(data={}, message=None, success=None, code=None, operation=None):

    code = code or 200

    if code in [200, 201, 204]:
        return response_2xx(data=data, message=message, success=success, code=code, operation=operation)
    elif code in [400, 401, 403, 404]:
        return response_4xx(message=message, success=success, code=code)
    elif code in [500, 502, 503]:
        return response_5xx(message=message, success=success, code=code)


def response_4xx(message=None, success=None, code=None):
    status_codes = [400, 401, 403, 404]
    if success is None:
        success = False
    _msg = ""
    _data = {
        "success": False,
        "code": code
    }
    
    if code in [400]:
        _msg = message or "Invalid request." 
    elif code in [401]:
        _msg = message or "Unauthorized request."
    elif code in [403]:
        _msg = message or "Forbidden." 
    elif code in [404]:
        _msg = message or "Resource not found."
    
    _data.update({"message": _msg})

    return JSONResponse(content=_data, status_code=code)   


def response_5xx(message=None, success=None, code=None):
    status_codes = [500, 502, 503]
    if success is None:
        success = False
    _msg = ""
    _data = {
        "success": False,
        "code": code
    }
    
    if code in [502]:
        _msg = message or "Bad gateway."
    elif code in [503]:
        _msg = message or "Service unavailable." 
    else:
        _msg = message or "Internal server error."
    
    _data.update({"message": _msg})

    return JSONResponse(_data, status_code=code)


def response_2xx(data=None, message=None, success=None, code=None, operation=None):
    status_codes = [200, 201, 204]
    if success is None:
        success = True
    _msg = ""
    _data = {
        "success": success,
        "code": code
    }
    operation = operation or "fetched"
    default_msg = get_default_msg(operation)
    message = message or default_msg
    if not data:
        _data.update({"data": {}})
    else:
        _data.update({"data": data})
    
    if code in [200]:
        _msg = message or "Success."
    elif code in [201]:
        _msg = message or "Created."
    elif code in [204]:
        _msg = message or "No content."
    
    _data.update({"message": _msg})

    return JSONResponse(content=_data, status_code=code)


def get_default_msg(operation):
    success = constants.ResponseMsgCodes.get("success")
    return success.get(operation).get("message")


def resource_not_found(resource=None, data={}):
    resp_msg_codes = constants.ResponseMsgCodes.get("error")
    error_type = resp_msg_codes.get("resource_not_found")
    success = False
    status_code = error_type.get("code")
    msg = error_type.get("message")
    if resource:
        msg = "The requested {} not found.".format(resource.lower())
    return response(data=data, message=msg, success=success, code=status_code)


def success_response_generator(key="fetched"):
    success = constants.ResponseMsgCodes.get("success")
    gen_resp = {"code": 200, "message": ""}
    if key and isinstance(key, str):
        gen_resp = success.get(key)
        return gen_resp
    return gen_resp


def invalid_request_response(data={}):
    resp_msg_codes = constants.ResponseMsgCodes.get("error")
    error_type = resp_msg_codes.get("invalid_request")
    success = False
    status_code = error_type.get("code")
    msg = error_type.get("message")
    return response(data=data, message=msg, success=success, code=status_code)


def try_except_err_response(message=None):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response(message=message, code=status_code)
