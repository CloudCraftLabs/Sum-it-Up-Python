import os
from dotenv import load_dotenv

APP_ROOT=os.getcwd()
dotenv_path = os.path.join(APP_ROOT, '.env')
# load dotenv in the base root
load_dotenv(dotenv_path)

env = os.getenv("ENVIRONMENT")

try:
    params = {}
    from .params_common import params as paramsAll
    if env is not None:
        envFinal = env.lower().replace("-", "_")
        _env_params_import_statement = f"from .params_{envFinal} import params as params2"
        print(f"Params command used : {_env_params_import_statement}")
        exec(_env_params_import_statement)
    else:
        print("Params command used local in else as not found env")
        from .params_local import params as params2
    
    params = { **paramsAll, **params2 }
except ImportError as err:
    print("Failed to import params")
except Exception as err:
    print(err)


# params = {
#     "AWSRegion" : "us-west-1",
#     'project-env':'zenarate/dev-tc', # <zenarate/dev-tc>/local
#     "logDir": "temp/logs",
#     "logMaxSize": 20000,
#     "logBackupFileCount": 20,
#     "loggerVersion": 1,
#     "AWSRegionSES": "us-west-1",
# }