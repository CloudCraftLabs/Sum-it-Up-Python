from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from src.config.database.database import Base

from fastapi_sqlalchemy import db
from sqlalchemy import CHAR, Column, Date, DateTime, Enum, Float, DECIMAL, ForeignKey, LargeBinary, String, TIMESTAMP, \
    Table, Text, text, BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM, BIGINT, INTEGER, LONGBLOB, LONGTEXT, MEDIUMTEXT, TINYINT, VARCHAR, JSON
from sqlalchemy.sql.sqltypes import Integer


class UrlSummaryHistory(Base):
    __tablename__ = 'url_summary_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    response_text = Column(BLOB)
    created_datetime = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    summary_type = Column(Enum('factual', 'keywords', 'abstractive'))


class FlowchartSummaryHistory(Base):
    __tablename__ = 'flowchart_summary_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    flowchart = Column(Text)
    created_datetime = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
