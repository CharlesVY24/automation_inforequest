from typing import Union, Annotated

from .automations.tenders_automation import fetch_data
from fastapi import  Depends, FastAPI, HTTPException, Query

from sqlmodel import select
from .models.tenders_model import create_db_and_tables, SessionDep, Tenders

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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