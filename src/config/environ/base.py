import os
import json
# from src.utils.common.aws import aws_services
import urllib.parse as up
# from src.utils.common.logger import logger
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '../../..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


class BaseConfig(object):        
    '''
        Function to get db string according to the environment 
    '''
    mysql_driver = "mysql+mysqlconnector://"

    def get_db_connection_string(self, dbtype="", env=None):
        _database_url = ""
        _ssl_file=os.getenv(dbtype.upper() + '_DB_SSL_FILE')

        
        if (env == None):
            env = os.getenv("ENVIRONMENT")
        
        if (env == "local"):
            dbUsername=os.getenv(dbtype.upper() + '_DB_USERNAME')
            dbPassword=up.quote(os.getenv(dbtype.upper() + '_DB_PASSWORD'))
            dbName=os.getenv(dbtype.upper() + '_DB_NAME')
            dbHost=os.getenv(dbtype.upper() + '_DB_HOST')
            dbPort=os.getenv(dbtype.upper() + '_DB_PORT')
            _database_url = self.mysql_driver + str(dbUsername) + ':' + str(dbPassword) + '@' + str(dbHost) + ':' + str(dbPort) + '/' + str(dbName)
        else :
            print("\n*********** Unable to connect DB ***********\n")
            # try:
                # Think twice before modifying it.
                # json_url = os.path.join(APP_ROOT, "src/config/database/json", dbtype.lower() + ".json")
                # is_file_exist = os.path.isfile(json_url)
                # if is_file_exist:
                #     print("Reading from file..................")
                #     data = json.load(open(json_url))
                # else:
                #     print(f"DB({dbtype}) File being reloaded from secret manager..................")
                #     secret = aws_services.getDBSecretValue(dbtype)
                #     logger.info(f"secret: {secret}")
                #     with open(json_url, 'w') as f:
                #         f.write(secret)
                #         print("=== Writing secret==")
                # data = json.load(open(json_url))

                # _database_url = self.mysql_driver + str(data['username']) + ':' + str(up.quote(data['password'])) + '@' + str(data['host']) + ':' + str(data['port']) + '/' + str(data['dbname'])

            # except Exception as e:
                # dbUsername=os.getenv(dbtype.upper() + '_DB_USERNAME')
                # dbPassword=up.quote(os.getenv(dbtype.upper() + '_DB_PASSWORD'))
                # dbName=os.getenv(dbtype.upper() + '_DB_NAME')
                # dbHost=os.getenv(dbtype.upper() + '_DB_HOST')
                # dbPort=os.getenv(dbtype.upper() + '_DB_PORT')
                # _database_url = self.mysql_driver + str(dbUsername) + ':' + str(dbPassword) + '@' + str(dbHost) + ':' + str(dbPort) + '/' + str(dbName)

        # if ((_ssl_file != "") and (_ssl_file != None)) :
        #     _database_url += '?ssl_ca=' + APP_ROOT + '/' + _ssl_file
        print("\n*********** Connected to DB ***********\n")
        return _database_url
