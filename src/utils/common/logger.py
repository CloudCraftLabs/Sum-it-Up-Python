import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from src.config.data import params
from . import utils


APP_ROOT = os.path.join(os.path.dirname(__file__), '../../..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')

# load dotenv in the base root
load_dotenv(dotenv_path)

def config_logger(data={}):
    log_dir_path = params.params.get("logDir")
    log_file_name = '{}_audits.log'
    log_dir = os.path.join(APP_ROOT, log_dir_path)
    # log_dir = os.path.join(os.path.dirname(__file__), '..', log_dir_path)
    backup_count = params.params.get("logBackupFileCount")
    max_file_size = params.params.get("logMaxSize")

    host_name = os.getenv("host_name")
    if host_name is None:
        host_name = data.get("host_name")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create the file handlers
    log_file = os.path.join(log_dir, log_file_name.format(host_name))
    file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=max_file_size, backupCount=backup_count, encoding='utf-8', delay=False)
    file_handler.setLevel(logging.INFO)

    # set formatter
    # '[%(asctime)s] - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s' for reference
    formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s :: %(message)s')
    file_handler.setFormatter(formatter)

    # clear all existing file_handlers
    if len(logger.handlers) > 0:
        logger.handlers.clear()
    # add file handler
    logger.addHandler(file_handler)

    return logger



default_host_name = utils.get_domain_name()
logger = config_logger(data={"host_name": default_host_name})
