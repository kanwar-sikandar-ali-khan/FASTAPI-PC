# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from app.models import Parent,ParentRequest,Child




def checkExistParent(*, session: Session, cnic_number: str) -> Parent | None:
    statement = select(Parent).where(Parent.cnic_number == cnic_number)
    session_user = session.exec(statement).first()
    return session_user
    

def create_parent(*, session: Session, parentObj: Parent) -> Parent:
    session.add(parentObj)
    session.commit()
    session.refresh(parentObj)
    return parentObj

def create_child(*, session: Session, childRow: Child) -> Child:
    session.add(childRow)
    session.commit()
    session.refresh(childRow)
    return childRow