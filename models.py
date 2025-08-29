from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
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


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("session.session_id"))
    message_user = Column(String)
    response_bot = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
