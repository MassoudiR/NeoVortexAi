from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import random
from g4f.client import Client
from enum import Enum
from models import ChatHistory , ChatSession
from database import Base , engine ,  get_db 

class Model(str, Enum):
    gpt_5 = 'gpt-5-nano'
    gpt_4_nano = 'gpt-4.1-nano'
    deepseek = 'deepseek-r1-0528'
    ai = 'openai-fast'
    mistral = 'mistral-small-3.1-24b'
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4 = "gpt-4"
    gemini_2_5 = 'gemini-2.5-flash-lite'
    gemini_pro = "gemini-2.5-flash"


default_model = Model.gpt_4_nano


app = FastAPI()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/create_session")
def create_session(db: Session = Depends(get_db)):
    """Create a new chat session and return its ID."""
    new_session = ChatSession()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.session_id}


@app.get("/chat")
def chat_with_bot(
    session_id: int,
    message: str,
    model: Model = default_model,
    db: Session = Depends(get_db),
    system: bool = False
):
    """/chat?session_id=xxx&message=hello&model=gpt_4_nano"""

    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    # Save system prompt
    if system:
        history_entry = ChatHistory(
            session_id=session_id,
            is_system_prompt=True,
            system_prompt=message
        )
        db.add(history_entry)
        db.commit()
        return 

    # Collect history
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.id).all()
    messages = []
    for h in history:
        if h.is_system_prompt:
            messages.append({"role": "system", "content": h.system_prompt})
        else:
            if h.message_user:
                messages.append({"role": "user", "content": h.message_user})
            if h.response_bot:
                messages.append({"role": "assistant", "content": h.response_bot})

    messages.append({"role": "user", "content": message})

    # Call the LLM client
    client = Client()
    response = client.chat.completions.create(
        model=model.value,
        messages=messages,
        web_search=False
    )
    bot_reply = response.choices[0].message.content

    # Save chat history
    history_entry = ChatHistory(
        session_id=session_id,
        message_user=message,
        response_bot=bot_reply
    )
    db.add(history_entry)
    db.commit()

    return {"session_id": session_id, "user": message, "bot": bot_reply, "model_used": model}


@app.get("/history/{session_id}")
def get_history(session_id: int, db: Session = Depends(get_db)):
    """Full chat history"""
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.id).all()
    return [
        {"user": h.message_user, "bot": h.response_bot, "time": h.created_at} if not  h.is_system_prompt else {"system": h.system_prompt, "time": h.created_at}
        for h in history
    ]


@app.get("/reset_db")
def reset_db():
    """⚠️ Dev only: Drop and recreate all tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "Database reset successful"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
