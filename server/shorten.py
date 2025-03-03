from typing import Annotated

from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from fastapi import Depends
import random
import string

class URL(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    short: str = Field(unique=True, index=True, nullable=False)
    long: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

sqlite_file_name = "shortener.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def get_short_url(long_url: str, session: SessionDep) -> str:
    statement = select(URL).where(URL.long == long_url)
    short_url = session.exec(statement).first()
    if short_url:
        return short_url.short

    return generate_short_url(long_url, session)

def generate_short_url(long_url: str, session: SessionDep) -> str:
    while True:
        s = string.ascii_letters + string.digits
        short_url = ''.join(random.sample(s,10))
        statement = select(URL).where(URL.short == short_url)
        if session.exec(statement).first():
            print(session.exec(statement))
            continue
        new_entry = URL(short=short_url, long=long_url)
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        return short_url

def get_long_url(short_url: str, session: SessionDep) -> str | None:
    statement = select(URL).where(URL.short == short_url)
    long_url = session.exec(statement).first()
    if long_url:
        return long_url.long
    return None
