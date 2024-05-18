import os
from dotenv import load_dotenv, dotenv_values
from src.config.environ import base

APP_ROOT = os.path.join(os.path.dirname(__file__), '../..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')

# load dotenv in the base root
load_dotenv(dotenv_path)
env_config = dotenv_values(".env")


from enum import Enum
DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
UI_DATE_FORMAT = "%d %b %Y"

BASE_URL = "https://{}/index.php"


TokenResponse = {
    "expired": {
      "message": "Token expired.",
      "status": False,
      "status_code": 401
    },
    "invalid": {
      "message": "Invalid token.",
      "status": False,
      "status_code": 401
    },
    "unknown": {
      "message": "unknown error.",
      "status": False, 
      "status_code": 400
    }
}

ResponseMsgCodes ={
  "success": {
    "created": {
        "code": 201,
        "message": "Data created successfully."
    },
    "updated": {
        "code": 200,
        "message": "Data updated successfully."
    },
    "fetched": {
        "code": 200,
        "message": "Data fetched successfully."
    },
    "deleted": {
        "code": 200,
        "message": "Data deleted successfully."
    }
  },
  "error": {
    "unknown_error": {
      "code": 500,
      "message": "An unknown error occurred."
    },
    "invalid_request": {
      "code": 400,
      "message": "Invalid request data."
    },
    "unauthorized": {
      "code": 403,
      "message": "Unauthorized access."
    },
    "resource_not_found": {
      "code": 404,
      "message": "The requested resource not found."
    },
    "database_error": {
      "code": 500,
      "message": "A database error occurred."
    }
  }
}



class AppLevelConstants:
    MODULE_ID = 4
    TOKEN_EXP_TIME = int(env_config.get("JWT_ACCESS_TOKEN_EXPIRES"))

EST_TIME_DICT = {"gmt_code": "GMT-5:00", "hours": -5}

TIMEOUT = 15
SPEECH_TIMEOUT = 2
ENABLE_CANNED_RESPONSE = '0'
STORY_DEFAULT_LANG = 'en-US'
DEFAULT_LANGUAGE_CODE = 'en-US'


LOCAL_BASE_URL = "http://{}/summary-app/api/v1"
GLOBAL_BASE_URL = "https://{}/summary-app/api/v1"

class TextSummmarizerErrorMessages:
    GenerateSummaryViaUrl = "Something Went Wrong While Generating Summary Via URL. ({})"
    GenerateSummaryViaText = "Something Went Wrong While Generating Summary Via Text. ({})"
    GenerateSummaryFlowchart = "Something Went Wrong While Generating Summary Flowchart. ({})"
    CheckUrlAuthorization = "Something Went Wrong While Checking URL Authorization. ({})"
    DownloadPDF = "Something Went Wrong While Downloading PDF. ({})"
    SearchAbout = "Something Went Wrong While Searching About Service. ({})"



class AuthErrorMessages:
    login = "Something Went Wrong While Login. ({})"
    generate_refresh_token = "Something Went Wrong While generating refresh_token . ({})"
    get_csrf_token = "Something Went Wrong While retrieving csrf_token . ({})"
    logout = "Something Went Wrong While Logout. ({})"

class CommmonErrorMessages:
    commit_log = "Something Went Wrong While Commiting Logs. ({})"

CHARSET = "UTF-8"
MICROSERVICE = "text_summarizer_app"
ENV = 'venv'

DEFAULT_PHPSESSION_ID = "QWERTYUIOPASDFGHJKLZXCVBNM"


status_code_mapper = {
    200: "Done",
    202: "Done",
    204: "Done",
    400: "Bad Request due to an error in the request URI, headers, or body",
    403: "You may have passed an invalid api-key",
    404: "Requested resource doesn't exist on the server",
    409: "Write operations conflict, maybe others are also writing simultaneously",
    429: "Too Many Requests",
    502: "Bad Gateway Error",
    503: "Service Unavailable due to heavy load on the server",
    504: "Gateway Timeout Error"
}


gemini_failure_responses = [
            "I am sorry, I do not have access to the internet and cannot summarize the content of the provided URL.",
            "I lack the ability to access the internet or specific web pages, including the one you provided from Zenarate. I am unable to provide a summary of the content on that webpage.",
            "I apologize, but I do not have access to the internet and am unable to fulfill your request to summarize the content of the webpage you provided.",
            "I apologize, but I do not have access to the internet and cannot provide a summary of the webpage content at the provided URL.",
            "I lack the ability to access the internet, including the URL you provided, and therefore cannot summarize the content of the webpage you referenced."
            ]

intent_list = [
                  "do not have access", 
                  "don't have access", 
                  "cannot retrieve the content", 
                  "lack the ability to access", 
                  "not able to access", 
                  "cannot provide a summary", 
                  "unable to access",
                  "cannot access",
                  "I apologize",
                  "I am sorry",
                  "cannot summarize",
                  "unable to summarize",
                  "unable_access",
                  "don't have the ability to access",
                  "unable to complete the task"
               ]


def url_task_mapper(body, summary_type):
  
  task_mapper = {
  "keywords": f"list the keywords from the summarized data of the content of webpage url: {body} in good quality.",
  "factual": f"Give a short factual summary of the content of webpage url: {body} in good quality. Please keep it clear and concise!",
  "abstractive": f"Give a abstractive summary of the content of webpage url: {body} in good quality. Please keep it clear and concise!"
  }
  result = task_mapper.get(summary_type) if summary_type in task_mapper else f"Summarize the content of the webpage in concise and clear manner, given in the url {body} in a good quality."
  return result 

def text_task_mapper(body, summary_type):
  
  task_mapper = {
  "keywords": f"list the keywords from the summarized data of the content of paragraph in short and good quality : {body}",
  "factual": f"Give a short factual summary of the content of given paragraph in short and good quality : {body}",
  "abstractive": f"Give a abstractive summary of the content of given paragraph in short and good quality : {body}"
  }
  result = task_mapper.get(summary_type) if summary_type in task_mapper else f"Summarize the content of the paragraph in concise and clear manner: {body}"
  return result 

def flowchart_task_mapper(body):
  result = f"explain the summary in the form of flowchart for the content of webpage url: {body} in good quality"
  return result


def search_about_task_mapper(body):
  result = f"Explain '{body}' in 3 lines."
  return result
