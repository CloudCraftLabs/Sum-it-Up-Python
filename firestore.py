import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import urllib.parse


cred = credentials.Certificate('sum-it-up-69082-bcdeaae82a95.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()


async def add_url(collection, url: str, summary: str, summary_type: str):
    encoded_url = urllib.parse.quote(url, safe='')
    new_url = encoded_url +"|"+summary_type
    doc_ref = db.collection(collection).document(new_url)
    doc_ref.set({
        'url': new_url,
        'summary': summary,
        'summary_type': summary_type,
        'created_at': firestore.SERVER_TIMESTAMP
    })


async def get_url(collection, url: str):
    encoded_url = urllib.parse.quote(url, safe='')
    doc_ref = db.collection(collection).document(encoded_url)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None


async def update_url(collection, url: str, summary: str, summary_type: str):
    encoded_url = urllib.parse.quote(url, safe='')
    new_url = encoded_url +"|"+summary_type
    query = db.collection(collection).where("url", "==", new_url).where("summary_type", "==", summary_type).limit(1)
    docs = query.stream()
    for doc in docs:
        doc_ref = doc.reference
        doc_ref.update({'summary': summary})
        doc_ref.update({'created_at': firestore.SERVER_TIMESTAMP})
        return True
    return False


async def get_url_with_summary_type(collection, url: str, summary_type: str):
    encoded_url = urllib.parse.quote(url, safe='')
    new_url = encoded_url +"|"+summary_type
    query = db.collection(collection).where("url", "==", new_url).where("summary_type", "==", summary_type)
    docs = query.limit(1).get()
    return docs[0].to_dict() if len(docs) > 0 and docs[0].exists else None
    
    
async def delete_url(collection, url: str, summary_type: str):
    encoded_url = urllib.parse.quote(url, safe='')
    new_url = encoded_url +"|"+summary_type
    query = db.collection(collection).where('url', '==', new_url).where('summary_type', '==', summary_type)
    docs = query.stream()    
    for doc in docs:
        doc.reference.delete()
        return True
    return False  

