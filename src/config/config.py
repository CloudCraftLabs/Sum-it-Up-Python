import os
from dotenv import load_dotenv, dotenv_values
from src.config.environ import base


APP_ROOT = os.path.join(os.path.dirname(__file__), '../..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')

# load dotenv in the base root
load_dotenv(dotenv_path)
env_config = dotenv_values(".env")



class Settings:
    TITLE = "text_summarizer_app"
    VERSION = "1.0.0"
    DESCRIPTION = """This project belongs to Karan & Prashansa"""
    NAME = "Karan And Prashansa"
    EMAIL = "kaykay9464769@gmail.com"
    SECRET_KEY = env_config.get("SECRET_KEY")
    ALGORITHM = env_config.get("ALGORITHM")
    username = env_config.get("username")
    password = env_config.get("password")
    host = env_config.get("host")
    database = env_config.get("database")
    environment = env_config.get("ENVIRONMENT")
    app_settings = env_config.get("APP_SETTINGS")
    base_config_obj = base.BaseConfig()
    database_url = base_config_obj.get_db_connection_string(dbtype="main")

settings = Settings()
