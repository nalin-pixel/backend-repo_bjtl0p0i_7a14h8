import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Dapp, Comment

app = FastAPI(title="Web3 Dapp Discovery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(str):
    pass

def to_serializable(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if doc.get("_id"):
        doc["id"] = str(doc.pop("_id"))
    # convert datetime to isoformat if present
    for k, v in list(doc.items()):
        try:
            import datetime
            if isinstance(v, (datetime.datetime, datetime.date)):
                doc[k] = v.isoformat()
        except Exception:
            pass
    return doc

@app.get("/")
def read_root():
    return {"message": "Web3 Dapp Discovery API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or ""
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Schemas endpoint for Flames viewer
@app.get("/schema")
def get_schema():
    from schemas import User, Dapp, Comment, Product
    return {
        "user": User.model_json_schema(),
        "dapp": Dapp.model_json_schema(),
        "comment": Comment.model_json_schema(),
        "product": Product.model_json_schema(),
    }

# Request models for specific endpoints
class VoteRequest(BaseModel):
    dapp_id: str

# Dapp endpoints
@app.post("/dapps")
def create_dapp(dapp: Dapp):
    try:
        dapp_id = create_document("dapp", dapp)
        return {"id": dapp_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dapps")
def list_dapps(category: Optional[str] = None, chain: Optional[str] = None):
    filt = {}
    if category:
        filt["category"] = category
    if chain:
        filt["chains"] = {"$in": [chain]}
    docs = get_documents("dapp", filt, limit=100)
    return [to_serializable(d) for d in docs]

@app.get("/dapps/{dapp_id}")
def get_dapp(dapp_id: str):
    try:
        doc = db["dapp"].find_one({"_id": ObjectId(dapp_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Dapp not found")
        return to_serializable(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/dapps/{dapp_id}/vote")
def vote_dapp(dapp_id: str):
    try:
        result = db["dapp"].update_one({"_id": ObjectId(dapp_id)}, {"$inc": {"votes": 1}, "$set": {"updated_at": __import__('datetime').datetime.utcnow()}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Dapp not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Comments
@app.post("/comments")
def create_comment(comment: Comment):
    try:
        # ensure dapp exists
        _ = db["dapp"].find_one({"_id": ObjectId(comment.dapp_id)})
        if _ is None:
            raise HTTPException(status_code=404, detail="Dapp not found")
        cid = create_document("comment", comment)
        return {"id": cid}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comments")
def list_comments(dapp_id: str):
    docs = get_documents("comment", {"dapp_id": dapp_id}, limit=200)
    return [to_serializable(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
