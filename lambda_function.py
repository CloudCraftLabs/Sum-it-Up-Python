import json
import os
import requests
import google.generativeai as genai
import asyncio
from fastapi import Depends, HTTPException, Request
from firestore import db, add_url, get_url, get_url_with_summary_type, delete_url, update_url
from datetime import datetime, timedelta


def lambda_handler(event, context):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_lambda_handler(event, context))
    return result


async def async_lambda_handler(event, context):
    body = json.loads(event['body'])

    if body and 'rawPath' in event and event['rawPath'] == "/summary-via-url" and event["body"] != {}:
        text_url = body.get("text_url")
        summary_type = body.get("summary_type")
        html_data = body.get("html_data")
        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=1, body=text_url,
                                                                                 summary_type=summary_type, html_data=html_data)

    elif body and 'rawPath' in event and event['rawPath'] == "/summary-via-text" and event["body"] != {}:
        body = json.loads(event['body'])
        text_url = body.get("text_url")
        summary_type = body.get("summary_type")
        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=2, body=text_url,
                                                                                 summary_type=summary_type)

    elif body and 'rawPath' in event and event['rawPath'] == "/summary-via-flowchart" and event["body"] != {}:
        body = json.loads(event['body'])
        text_url = body.get("text_url")
        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=3, body=text_url)

    elif body and 'rawPath' in event and event['rawPath'] == "/search-about" and event["body"] != {}:
        body = json.loads(event['body'])
        text = body.get("text")
        status_code, response_data = await search_about(text=text)

    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Invalid Request!')
        }
    
    response = {"data": response_data, "statusCode": status_code, "status": "success" if status_code == 200 or status_code == 201 else "failed"}
    print("Response: ", response)
    return {
        'statusCode': status_code,
        'body': json.dumps(response)
    }


async def search_about(text):
    try:
        task = search_about_task_mapper(text)
        response = await gemini_request_for_task(task=task)

        if response.status_code != 200 and response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.status_code, response.json().get("candidates")[0]["content"]["parts"][0]["text"]

    except Exception as err:
        raise err


async def summary_via_webscrap(html_data):
    try:
        task = webscrap_task_mapper(html_data)
        response = await gemini_request_for_task(task=task)

        if response.status_code != 200 and response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.status_code, response.json().get("candidates")[0]["content"]["parts"][0]["text"]

    except Exception as err:
        raise err


async def generate_text_summary_via_url_or_text(body_flag, body, summary_type="factual", html_data=""):
    try:

        task = None
        delete_url_status = True
        collection = os.environ.get("COLLECTION")

        if body_flag == 1:
            result_obj = await get_url_with_summary_type(collection, body, summary_type)
            if result_obj is not None:
                time_period = await check_time_exceeded(result_obj['created_at'])
                if time_period is False:
                    return 200, result_obj['summary']
                elif time_period is True:
                    delete_url_status = await delete_url(collection, body, summary_type)
                    print("delete_url_status:", delete_url_status)

            task = url_task_mapper(body, summary_type)

        elif body_flag == 2:
            task = text_task_mapper(body, summary_type)

        elif body_flag == 3:
            task = flowchart_task_mapper(body)

        response = await gemini_request_for_task(task=task)

        if response.status_code != 200 and response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        if "content" not in response.json().get("candidates")[0]:
            print(response.json())
            return response.status_code, response.json()
            
        response_data = response.json().get("candidates")[0]["content"]["parts"][0]["text"]
        unable_access_response_flag = await detect_intent(response_data)
        if unable_access_response_flag == "unable_access":
            response_data = "UNABLE ACCESS"

        if body_flag == 1:
            # if unable_access_response_flag == "unable_access":
            #     webscrap_status, webscrap_response = await summary_via_webscrap(html_data)
            #     response_data = webscrap_response.json().get("candidates")[0]["content"]["parts"][0]["text"]
            
            if response.status_code == 200 and unable_access_response_flag != "unable_access":
                if delete_url_status is True:
                    await add_url(collection, body, response_data, summary_type)
                else:
                    update_url_status = await update_url(collection, body, response_data, summary_type)

        return response.status_code, response_data

    except Exception as err:
        raise err


async def gemini_request_for_task(task):
    try:

        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": {"role": "USER", "parts": {"text": task}}}
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            headers=headers, json=payload)
        print("\n\nGemini Result: ", response.json(), "\n\n")
        return response
    except Exception as err:
        raise err


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
    "I lack the ability to access the internet, including the URL you provided, and therefore cannot summarize the content of the webpage you referenced.",
    "I did not find any details about ENI lifecycle on the provided webpage."
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
    "unable to complete the task",
    "did not find any details",
    "unable to find any details"
]


def url_task_mapper(body, summary_type):
    task_mapper = {
        "keywords": f"list the keywords from the summarized data of the content of webpage url: {body} in good quality.",
        "factual": f"Give a short factual summary of the content of webpage url: {body} in good quality. Please keep it clear and concise!",
        "abstractive": f"Give a abstractive summary of the content of webpage url: {body} in good quality. Please keep it clear and concise!"
    }
    result = task_mapper.get(
        summary_type) if summary_type in task_mapper else f"Summarize the content of the webpage in concise and clear manner, given in the url {body} in a good quality."
    return result


def text_task_mapper(body, summary_type):
    task_mapper = {
        "keywords": f"list the keywords from the summarized data of the content of paragraph in short and good quality : {body}",
        "factual": f"Give a short factual summary of the content of given paragraph in short and good quality : {body}",
        "abstractive": f"Give a abstractive summary of the content of given paragraph in short and good quality : {body}"
    }
    result = task_mapper.get(
        summary_type) if summary_type in task_mapper else f"Summarize the content of the paragraph in concise and clear manner: {body}"
    return result


def flowchart_task_mapper(body):
    result = f"explain the summary in the form of flowchart for the content of webpage url: {body} in good quality"
    return result
    
    
def webscrap_task_mapper(body):
    result = f"I am giving you an outer html page to you. I want you to webscrap the content and summarize the content by ignoring unwanted informations and ads etc. '{body}'"
    return result    


def search_about_task_mapper(body):
    result = f"Explain '{body}' in 3 lines."
    return result

async def detect_intent(text: str):
    for intent in intent_list:
        if intent in text:
            print("\nLength of Failure Response: ", len(text),"\n")
            return "unable_access"
    return None


async def check_time_exceeded(time_xyz):
    if isinstance(time_xyz, datetime):
        current_time = datetime.now(time_xyz.tzinfo)
        time_difference = current_time - time_xyz
        if time_difference > timedelta(hours=24):
            return True
    return False
