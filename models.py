from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey , Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import random
from g4f.client import Client
from enum import Enum 
from database import Base

class ChatSession(Base):
    __tablename__ = "session"

    session_id = Column(Integer, primary_key=True, index=True,
                        default=lambda: random.randint(100000, 999999))
    created_at = Column(DateTime, default=datetime.utcnow)


from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import random

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "session"

    session_id = Column(Integer, primary_key=True, index=True,
                        default=lambda: random.randint(100000, 999999))
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("session.session_id"), nullable=False, index=True)
    is_system_prompt = Column(Boolean, default=False)
    system_prompt = Column(String, nullable=True)
    message_user = Column(String, nullable=True)
    response_bot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
