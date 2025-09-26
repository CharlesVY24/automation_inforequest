from typing import Union, Annotated

from automations.tenders_automation import fetch_data
from fastapi import  Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from sqlmodel import select
from models.tenders_model import create_db_and_tables, SessionDep, Tenders

app = FastAPI()

# CORS: configurable via ALLOWED_ORIGINS (comma-separated) env var
allowed = os.getenv("ALLOWED_ORIGINS")
if allowed:
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
else:
    # sensible default for dev: allow all. In production set ALLOWED_ORIGINS.
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        create_db_and_tables()
    except Exception as e:
        # Log and continue — DB may be external and misconfigured; fail fast is avoided here
        print(f"[ERROR] create_db_and_tables failed: {e}")

@app.post("/automation")
def read_root(
    session: SessionDep
):
    response = fetch_data()
    if not response or not response["data"]:
        raise HTTPException(status_code=404, detail="No data found")
    
    for tenderIterator in response["data"]:
        existing_tender = session.exec(
            select(Tenders).where(Tenders.referencia_del_proceso == tenderIterator["referencia_del_proceso"])).first()
       
        if existing_tender:
            for key, value in tenderIterator.items():
                setattr(existing_tender, key, value)
        else:
            tenderModel = Tenders(**tenderIterator)
            session.add(tenderModel)
            
    session.commit()
   
    return {
        "message": "Welcome to the Tender Automation API",
        "data": response["data"],
        "total": response["total"],
        "ok": True
    }



# @app.post("/tender-automation/")
# def create_hero(tender: Tenders, session: SessionDep):

#     session.add(tender)
#     session.commit()
#     session.refresh(tender)
#     return {
#         "message": "Hero created successfully",
#         "hero": tender,
#         "ok" : True
#     }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/diag")
def diag(request: Request):
    """Diagnostic endpoint that echoes some request headers to help debug CORS/network issues."""
    return {
        "client": request.client.host if request.client else None,
        "headers": {k: v for k, v in request.headers.items() if k.lower() in ["origin", "host", "referer", "user-agent"]},
    }