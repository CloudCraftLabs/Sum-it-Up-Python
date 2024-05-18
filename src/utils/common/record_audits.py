import os
import socket
import requests
import json
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from src.config.database.database import get_db
from src.utils.common.logger import logger, config_logger
from src.utils.common import constants
from src.config.config import settings
from . import helper
from src.utils.common import utils
from src.utils.common import datetime_utils as dtu


def get_ec2_instance_id():
    ec2_instance_id = None
    try:
        root="/home"
        file_path = os.path.join(root,"ubuntu","instancedata" + ".json")
        file_ptr = open(file_path, "r")
        if file_ptr:    
            file_data = file_ptr.read()
            file_ptr.close()
            json_data = json.loads(file_data)
            ec2_instance_id = json_data['ec2InstanceId']
    except Exception as e:
        return ec2_instance_id
    return ec2_instance_id


def record_audit(data, event_type=None, event_id=None, db:Session = Depends(get_db), request=None, log_type="info" ):
    session_id = None
    ip_address = None
    server_name = None    
    
    
    if (event_type == None):
        event_type = "default"

    if (event_id == None):
        event_id = log_type
        

    if server_name == None:
        server_name = "local_server"

    try:
        hostname = socket.gethostname()
        if (hostname):
            ip_address = socket.gethostbyname(hostname)
    except Exception as err:
        ip_address = "127.0.0.1"
    
    request_uri = None
    user_agent = None
  
    if (request):
        request_uri = f"{request.url.path}?{request.url.query}" if request.url.query else f"{request.url.path}"
        user_agent = str(request.headers.get('user-agent'))

    data = str(data)
    ec2_instance_id = "get_ec2_instance_id()"

    audit = {
        "log_type": log_type,
        "eventType" : event_type,
        "session_id" : session_id,
        "ec2_instance_id" : ec2_instance_id,
        "data" : data,
        "ip_address" : ip_address,
        "server_name" : server_name,
        "request_uri" : request_uri,
        "user_agent" : user_agent,
        "created_date" : dtu.get_datetime_db_format()
    }
    if type(hostname) == str:
        hostname = {"hostname":hostname}
    logger = config_logger(data=hostname)
    logger.info(json.dumps(audit))
    return None

