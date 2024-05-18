from fastapi import BackgroundTasks, Body, Depends, Request, Form, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.modules.text_summarizer_service.module import check_url_authorization, create_db_entry_for_flowchart, create_db_entry_for_url, generate_text_summary_via_url_or_text, search_about, text_to_speech
from src.config.database.database import get_db
from src.utils.common.responses.handlers.http_exceptions import exception_handler
from src.utils.common.responses.response import response, try_except_err_response
from src.utils.common.record_audits import record_audit
from src.utils.common.utils import format_text
from src.utils.common.constants import status_code_mapper
from src.utils.common.helper import detect_intent
from bleach import clean
from io import BytesIO
from reportlab.pdfgen import canvas
import tempfile
from reportlab.lib.pagesizes import letter  # Adjust page size as needed
from reportlab.lib import pagesizes 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch  
from reportlab.pdfbase.ttfonts import TTFont



async def generate_summary_via_url_service(request: Request, data: dict , db: Session = Depends(get_db)):
    
    try:
        record_audit(data={"data": data}, event_type=f'Inside generate_summary_via_url_service', log_type='info', db=db, request=request)
        
        if "text_url" not in data or data.get("text_url") == None or data.get("text_url") == "":
            return response(data="text_url is missing in the request", message="text_url is missing in the request", success=False, code=400)
        
        if "summary_type" not in data or data.get("summary_type") == None or data.get("summary_type") == "":
            return response(data="summary_type is missing in the request", message="summary_type is missing in the request", success=False, code=400)
                
        text_url = data.get("text_url")
        summary_type = data.get("summary_type") 
        
        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=1 ,request=request, body=text_url, db=db, summary_type=summary_type)
        response_status = True if status_code == 200 or status_code == 201 else False
        message = status_code_mapper[status_code] if status_code in status_code_mapper else "Success!"
        response_flag = await detect_intent(response_data)
        if response_flag == None:
            response_to_return = await create_db_entry_for_url(url = text_url, response_text = response_data, request = request, db = db, summary_type = summary_type)
            return response(data=response_to_return, message=message, success=response_status, code=status_code)  
        elif response_flag == "unable_access":
            return response(data="unable_access", message=message, success=response_status, code=status_code) 

    except Exception as err:
        message = exception_handler(module='text_summarizer', func='GenerateSummaryViaUrl',main_db=db, request=request)
        return try_except_err_response(message=message)
    
    
async def generate_summary_via_text_service(request: Request, data: dict , db: Session = Depends(get_db)):
    
    try:
        record_audit(data={"data": data}, event_type=f'Inside generate_summary_via_text_service', log_type='info', db=db, request=request)
        
        if "text_url" not in data or data.get("text_url") == None or data.get("text_url") == "":
            return response(data="text_url is missing in the request", message="text_url is missing in the request", success=False, code=400)
        
        if "summary_type" not in data or data.get("summary_type") == None or data.get("summary_type") == "":
            return response(data="summary_type is missing in the request", message="summary_type is missing in the request", success=False, code=400)
                
        text = data.get("text_url")
        summary_type = data.get("summary_type") 
        
        text = clean(text)
        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=2 ,request=request, body=text, db=db, summary_type=summary_type)
        response_status = True if status_code == 200 or status_code == 201 else False
        message = status_code_mapper[status_code] if status_code in status_code_mapper else "Success!"
        response_flag = await detect_intent(response_data)
        if response_flag == None:
            return response(data=response_data, message=message, success=response_status, code=status_code)  
        elif response_flag == "unable_access":
            return response(data="unable_access", message=message, success=response_status, code=status_code)   
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='GenerateSummaryViaText',main_db=db, request=request)
        return try_except_err_response(message=message)    
    
    
async def generate_summary_flowchart_service(request: Request, data: dict , db: Session = Depends(get_db)):
    
    try:
        record_audit(data={"data": data}, event_type=f'Inside generate_summary_flowchart_service', log_type='info', db=db, request=request)
        
        if "text_url" not in data or data.get("text_url") == None or data.get("text_url") == "":
            return response(data="text_url is missing in the request", message="text_url is missing in the request", success=False, code=400)
        
        text_url = data.get("text_url")

        status_code, response_data = await generate_text_summary_via_url_or_text(body_flag=3 ,request=request, body=text_url, db=db)
        response_status = True if status_code == 200 or status_code == 201 else False
        message = status_code_mapper[status_code] if status_code in status_code_mapper else "Success!"
        response_flag = await detect_intent(response_data)
        if response_flag == None:
            response_to_return = await create_db_entry_for_flowchart(url = text_url, response_text = response_data, request = request, db = db)
            return response(data=response_to_return, message=message, success=response_status, code=status_code)  
        elif response_flag == "unable_access":
            return response(data="unable_access", message=message, success=response_status, code=status_code)  
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='GenerateSummaryFlowchart',main_db=db, request=request)
        return try_except_err_response(message=message)   
    
async def check_url_authorization_service(request: Request, data: dict , db: Session = Depends(get_db)):
    try:
        text_url = data.get("text_url")
        url_authorization_status, url_authorization_status_code = await check_url_authorization(url=text_url, db=db)
        return response(data=url_authorization_status, message="success", success="True", code=url_authorization_status_code) 
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='CheckUrlAuthorization',main_db=db, request=request)
        return try_except_err_response(message=message)  
    
async def download_pdf(request: Request, text: str = Form(...) , db: Session = Depends(get_db)):
    try:
        
        if not text:
            return response(data="Text content is required", message="Failed", success=False, code=400) 
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create a PDF document in memory
            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer)

            # Set font and font size
            pdf.setFont("Helvetica", 12)

            # Maximum line length (adjust as needed)
            max_line_length = 70  # Characters per line (including spaces)

            # Process text data line by line with line wrapping
            for line in text.splitlines():
                words = line.split()  # Split the line into individual words
                current_line = ""  # Current line being built
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_line_length:  # Check if word fits
                        current_line += word + " "  # Add word and space
                    else:
                        # Word doesn't fit, write current line to PDF and start a new one
                        pdf.drawString(50, 700, current_line.strip())  # Write the line (remove trailing space)
                        pdf.translate(0, -15)  # Move down for new line
                        current_line = word + " "  # Start new line with the word

                # Write the last line (if any)
                if current_line:
                    pdf.drawString(50, 700, current_line.strip())
                    pdf.translate(0, -15)

            # Save the PDF data
            pdf.save()
            pdf_buffer.seek(0)
            
            # Write the PDF data to the temporary file
            temp_file.write(pdf_buffer.getvalue())

            # Get the path to the temporary file
            temp_file_path = temp_file.name
            
        # Return the temporary file for download
        return FileResponse(
            temp_file_path,
            media_type="application/pdf",
            filename="text.pdf",
        )      
        
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='DownloadPDF',main_db=db, request=request)
        return try_except_err_response(message=message)   
    
    
async def text_to_speech_service( background_tasks: BackgroundTasks,request: Request,data: dict , db: Session = Depends(get_db)):
    try:
        text = data.get("text")
        
        response = await text_to_speech(text, background_tasks)
        response_status = True
        status_code = 200
        message = "Done"
        return response
        # return {"success": True, "status code": 200, "message": "Done!"} 
    
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='DownloadPDF',main_db=db, request=request)
        return try_except_err_response(message=message)    
          
    
async def search_about_service(request: Request,data: dict , db: Session = Depends(get_db)):
    try:
        
        record_audit(data={"data": data}, event_type=f'Inside search_about_service', log_type='info', db=db, request=request)
        if "text" not in data or data.get("text") == None or data.get("text") == "":
            return response(data="text is missing in the request", message="text is missing in the request", success=False, code=400)

        text = data.get("text")
        
        status_code, response_data = await search_about(text=text, request=request, db=db)
        response_status = True if status_code == 200 or status_code == 201 else False
        message = status_code_mapper[status_code] if status_code in status_code_mapper else "Success!"
        return response(data=response_data, message=message, success=response_status, code=status_code) 
    
    except Exception as err:
        message = exception_handler(module='text_summarizer', func='SearchAbout',main_db=db, request=request)
        return try_except_err_response(message=message)         