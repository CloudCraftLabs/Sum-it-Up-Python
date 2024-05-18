import time
from fastapi import Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
import requests
import os
import json
from src.models.models import FlowchartSummaryHistory, UrlSummaryHistory
from src.config.database.database import get_db
import google.generativeai as genai
from sqlalchemy.orm import Session
from src.utils.common.record_audits import record_audit
from gtts import gTTS
import pyttsx3
import playsound
import asyncio
from src.utils.common.constants import flowchart_task_mapper, search_about_task_mapper, text_task_mapper, url_task_mapper


async def generate_text_summary_via_url_or_text(body_flag, body, request: Request,  db: Session = Depends(get_db), summary_type = "factual"):
    try:
        record_audit(data={"site_body": body}, event_type=f'Inside generate_summary_via_url_service Method',log_type='info', db=db, request=request)

        summary_db_obj = None

        if body_flag == 1:
            
            summary_db_obj = db.query(UrlSummaryHistory).filter(UrlSummaryHistory.url == body, UrlSummaryHistory.summary_type == summary_type).order_by(UrlSummaryHistory.id.desc()).first()
            if summary_db_obj != None:
                if summary_db_obj.response_text != "":
                    return 200, summary_db_obj.response_text            
            task = url_task_mapper(body, summary_type)

        elif body_flag == 2:
            task = text_task_mapper(body, summary_type)

        elif body_flag == 3:
            summary_db_obj = db.query(FlowchartSummaryHistory).filter(FlowchartSummaryHistory.url == body).order_by(FlowchartSummaryHistory.id.desc()).first()
            if summary_db_obj != None:
                if summary_db_obj.flowchart != None and summary_db_obj.flowchart != "":
                    return 200, summary_db_obj.flowchart            
            task = flowchart_task_mapper(body)

        response = await gemini_request_for_task(task=task)

        if response.status_code != 200 and response.status_code != 201:
            record_audit(data={"data": response.json(), "status_code": response.status_code},event_type=f'Inside generate_summary_via_url_service Method-- Failed', log_type='error', db=db, request=request)
            raise HTTPException(status_code=response.status_code, detail=response.text)

        if "content" not in response.json().get("candidates")[0]:
            print(response.json())
            
        record_audit(data={"data": response.json(), "status_code": response.status_code},event_type=f'Inside generate_summary_via_url_service Method-- Success', log_type='info', db=db, request=request)            
        return response.status_code, response.json().get("candidates")[0]["content"]["parts"][0]["text"]

    except Exception as err:
        record_audit(data={}, event_type=f'Inside generate_summary_via_url_service Method-- Exception',log_type='error', db=db, request=request)
        raise err


async def gemini_request_for_task(task):
    try:
        API_KEY = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": {
                "role": "USER",
                "parts": {"text": task}
            }
        }

        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}", headers=headers, json=payload)
        return response
    except Exception as err:
        raise err


async def create_db_entry_for_url(url, response_text, summary_type, request: Request,  db: Session = Depends(get_db)):
    try:

        summary_db_obj = db.query(UrlSummaryHistory).filter(UrlSummaryHistory.url == url,
                                                            UrlSummaryHistory.summary_type == summary_type).order_by(UrlSummaryHistory.id.desc()).first()

        if summary_db_obj != None:

            if summary_db_obj.response_text == "":
                summary_db_obj.response_text = response_text
                db.commit()
                return response_text

            elif summary_db_obj.response_text != None and summary_db_obj.response_text != "":
                return summary_db_obj.response_text

        else:
            summary_data_obj = UrlSummaryHistory()
            summary_data_obj.url = url
            summary_data_obj.response_text = response_text
            summary_data_obj.summary_type = summary_type
            db.add(summary_data_obj)
            db.commit()
        return response_text

    except Exception as err:
        db.rollback()
        raise err


async def create_db_entry_for_flowchart(url, response_text, request: Request,  db: Session = Depends(get_db)):
    try:

        summary_db_obj = db.query(FlowchartSummaryHistory).filter(FlowchartSummaryHistory.url == url).order_by(FlowchartSummaryHistory.id.desc()).first()

        if summary_db_obj != None:

            if summary_db_obj.flowchart == "" or summary_db_obj.flowchart == None:
                summary_db_obj.flowchart = response_text
                db.commit()
                return response_text

            elif summary_db_obj.flowchart != None and summary_db_obj.flowchart != "":
                return summary_db_obj.flowchart

        else:
            summary_data_obj = FlowchartSummaryHistory()
            summary_data_obj.url = url
            summary_data_obj.flowchart = response_text
            db.add(summary_data_obj)
            db.commit()
        return response_text

    except Exception as err:
        db.rollback()
        raise err


async def check_url_authorization(url, db: Session = Depends(get_db)):
    try:

        summary_db_obj = db.query(UrlSummaryHistory).filter(
            UrlSummaryHistory.url == url).order_by(UrlSummaryHistory.id.desc()).first()
        if summary_db_obj == None:
            response = requests.post(url=url)

            if response.status_code == 200 or response.status_code == 201:
                url_status = "authorized"

                summary_db_obj = db.query(UrlSummaryHistory).filter(
                    UrlSummaryHistory.url == url, UrlSummaryHistory.url_status == url_status).order_by(UrlSummaryHistory.id.desc()).first()

                if summary_db_obj != None:
                    return url_status, response.status_code
                else:
                    summary_data_obj = UrlSummaryHistory()
                    summary_data_obj.url = url
                    summary_data_obj.response_text = ""
                    summary_data_obj.url_status = url_status
                    db.add(summary_data_obj)
                    db.commit()
                    return url_status, response.status_code
            return "unauthorized", response.status_code
        else:
            return summary_db_obj.url_status, 200
    except Exception as err:
        raise err


async def text_to_speech(text, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:

        asyncio.create_task(text_to_speech_helper(text,background_tasks))
        background_tasks.add_task(delete_temp_file, "output.mp3")
        return FileResponse("output.mp3", media_type="audio/mpeg", filename="output.mp3") 
        
    except Exception as err:
        raise err
      


async def text_to_speech_helper(text, background_tasks: BackgroundTasks):
    try:
        temp_file = 'output.mp3'
        language = 'en'
        tts = gTTS(text=text, lang=language)
        tts.save(temp_file)
        # await play_audio_file(temp_file)
        return temp_file

    except Exception as err:
        raise err
 
  

async def delete_temp_file(temp_file: str):

    if os.path.exists(temp_file):
        os.remove(temp_file)

async def play_audio_file(file_path: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, playsound.playsound, file_path)


async def search_about(text, request: Request, db: Session = Depends(get_db)):
    try:
        task = search_about_task_mapper(text)
        response = await gemini_request_for_task(task=task)

        if response.status_code != 200 and response.status_code != 201:
            record_audit(data={"data": response.json(), "status_code": response.status_code},event_type=f'Inside search_about Method-- Failed', log_type='error', db=db, request=request)
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        record_audit(data={"data": response.json(), "status_code": response.status_code},event_type=f'Inside search_about Method-- Success', log_type='info', db=db, request=request)            
        return response.status_code, response.json().get("candidates")[0]["content"]["parts"][0]["text"]   
         
    except Exception as err:
        record_audit(data={}, event_type=f'Inside search_about Method-- Exception',log_type='error', db=db, request=request)
        raise err
    