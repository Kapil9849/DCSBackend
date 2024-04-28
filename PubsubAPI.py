import json
from fastapi import Body, FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, List, Dict
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

class SNSNotification(BaseModel):
    Type: str
    MessageId: str
    Token: str
    TopicArn: str
    Message: str
    SubscribeURL: str
    Timestamp: str
    SignatureVersion: str
    Signature: str
    SigningCertURL: str

@app.post("/sns/notification")
async def receive_sns_confirmation(request: dict = Body(...)):
    # Verify that the request is a SubscriptionConfirmation
    # if notification.Type == "SubscriptionConfirmation":
    #     # Extract relevant information from the notification
    #     message_id = notification.MessageId
    #     token = notification.Token
    #     topic_arn = notification.TopicArn
    #     message = notification.Message
    #     subscribe_url = notification.SubscribeURL
    #     timestamp = notification.Timestamp
    #     signature_version = notification.SignatureVersion
    #     signature = notification.Signature
    #     signing_cert_url = notification.SigningCertURL
        
    #     # Perform any necessary processing or validation
        
    #     # Respond with a success message
    #     return {"status": "SubscriptionConfirmationReceived", "message_id": message_id}
    if(request):
        return request
    else:
        # Respond with an error for unknown message types
        raise HTTPException(status_code=400, detail="Unknown message type")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
