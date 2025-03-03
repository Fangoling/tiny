from typing import Annotated
from fastapi import FastAPI, Depends, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import shorten

class ShortenRequest(BaseModel):
    long_url: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.on_event("startup")
def on_startup():
    shorten.create_db_and_tables()

@app.get("/")
def read_root():
    return {"Hello": "This is an URL Shortener"}

@app.post("/shorten")
def shorten_url(request: ShortenRequest, session: shorten.SessionDep) -> shorten.URL:
    return { "short": shorten.get_short_url(request.long_url, session) }

@app.get("/{short_url}")
def redirect_to_long_url(short_url: str, session: shorten.SessionDep):
    long_url = shorten.get_long_url(short_url, session)
    if long_url:
        return RedirectResponse(f"{long_url}", status_code=303)
    return {"Error":"shortened url not found"} 
