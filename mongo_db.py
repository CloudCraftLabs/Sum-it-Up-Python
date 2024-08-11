# from mongoengine import Document, StringField, IntField, connect, DateTimeField, signals
# from datetime import datetime
# import os

# connect(host=os.environ.get("MONGO_URI"))  # Connect to your MongoDB database


# class UrlSummary(Document):
#     url = StringField(required=True)
#     summary = StringField(required=True)
#     summary_type = StringField()
#     created_at = DateTimeField(default=datetime.now())

#     def to_dict(self):
#         return {
#             "url": self.url,
#             "summary": self.summary,
#             "summary_type": self.summary_type,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }

#     @staticmethod
#     def pre_save(sender, document, **kwargs):
#         document.updated_at = datetime.now()


# signals.pre_save.connect(UrlSummary.pre_save, sender=UrlSummary)


# class UrlRepository:
#     @staticmethod
#     def find_by_url(url: str):
#         return UrlSummary.objects(url=url).first().to_json()

#     @staticmethod
#     def find_by_url_and_type(url: str, summary_type: str):
#         return UrlSummary.objects(url=url, summary_type=summary_type).first().to_json()

#     @staticmethod
#     def create_user(url: str, summary: str, summary_type: str):
#         url_data = UrlSummary(url=url, summary=summary, summary_type=summary_type)
#         url_data.save()
#         return url_data.to_json()
