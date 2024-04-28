import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Number of candidates
@app.on_event("startup")
async def Startup():
    pass



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
