import json
from fastapi import FastAPI, HTTPException, Request
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
    Message: str
    TopicArn: str

@app.post("/sns/notification")
async def sns_notification(request: Request, notification: SNSNotification):
    # AWS SNS sends notifications as HTTP POST requests with JSON payloads
    # You can access the JSON payload directly in the request body kapil
    print("kapil :",notification)
    request_body = await request.body()
    print("Received request payload:", request_body.decode())
    # Verify that the request is coming from AWS SNS
    # AWS SNS sends a subscription confirmation message which you should handle separately
    if notification.Type == "SubscriptionConfirmation":
        # Handle subscription confirmation here
        # Typically you'll need to visit the provided URL to confirm subscription
        subscription_url = notification.Message
        # You can also return a response indicating successful subscription confirmation
        return {"status": "SubscriptionConfirmation"}
    
    # Handle other types of notifications (e.g., actual messages)
    elif notification.Type == "Notification":
        # Do something with the notification message
        notification_message = notification.Message
        print("Received notification:", notification_message)
        # You can also return a response indicating successful notification processing
        return {"status": "NotificationReceived"}
    
    # Return an error response for unknown message types
    else:
        raise HTTPException(status_code=400, detail="Unknown message type")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
