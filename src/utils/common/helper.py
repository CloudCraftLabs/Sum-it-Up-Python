import gzip
import hashlib
import json
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from src.config.database.database import get_db
import spacy
from spacy.tokens import Doc    
from src.utils.common import utils
from src.utils.common.constants import intent_list


def luis_api_status_code(code):
    status_dict = {
        "400": "Invalid request.",
        "401": "Unauthorized request.",
        "403": "Total monthly key quota limit exceeded.",
        "409": "The ai application is still loading.",
        "410": "The application needs to be retrained and republished.",
        "414": "The query exceeds maximum character limit.",
        "429": "The rate limit is exceeded (requests/second).",
    }
    if str(code) in status_dict:
        return status_dict.get(str(code))
    else:
        return "Right now the AI application is unavailable to handle the request please try again after some time. Thank You!"



def hashConverter(element):
    '''
    this method will create hash keys for utterances and intents
    '''
    hashed_data = hashlib.sha256(element.encode()).hexdigest()
    return hashed_data


nlp = spacy.load("en_core_web_sm")

def get_intent(doc):

  for intent in intent_list:
    if intent in doc.text:
        return "unable_access"

  return None


async def detect_intent(text: str):

  doc = nlp(text)
  return get_intent(doc)


async def compress_and_store(text: str):
    """Compresses text compressed with gzip (client-side or server-side)."""
    return gzip.compress(text.encode("utf-8"))

def decompress_text(compressed_text):
    """Decompresses text compressed with gzip (client-side or server-side)."""
    return gzip.decompress(compressed_text).decode("utf-8")