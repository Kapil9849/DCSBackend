import json
from fastapi import Body, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from typing import Any, List, Dict
import random
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket,user_id:str):
        await websocket.accept()
        print(websocket.client)
        
        self.active_connections[user_id]=websocket

    def disconnect(self, websocket: WebSocket, user_id:str):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Number of candidates
@app.on_event("startup")
async def Startup():
    pass

class MessageAttributes(BaseModel):
    # Add attributes as needed
    pass

class SnsNotification(BaseModel):
    Type: str
    MessageId: str
    TopicArn: str
    Subject: str
    Message: str
    Timestamp: str
    SignatureVersion: str
    Signature: str
    SigningCertUrl: str
    UnsubscribeUrl: str
    MessageAttributes: MessageAttributes

class SportsUpdatesNotification(BaseModel):
    statusCode: int
    body: SnsNotification

class LoginModel(BaseModel):
    username:str
    password:str

@app.get("/users")
def getUsers():
    with open("assets/users.json", 'r') as file:
        users_data = json.load(file)
        return users_data

@app.post("/login")
def Login(loginModel:LoginModel):
    with open("assets/users.json", 'r') as file:
        users_data = json.load(file)
    for user in users_data:
        if(user["email"]==loginModel.username and user["password"]==loginModel.password):
            print("Login is success")
            data={
                "first_name":user["first_name"],
                "last_name":user["last_name"],
                "username":user["email"],
                "user_id": user["userId"]
            }
            return {"result":True,"data":data}
    else:
        return {"result":False,"data":"Login Failed !"}

@app.get("/getoptions")
def getOptions():
    with open("assets/options.json", 'r') as file:
        options = json.load(file)
    return {"result":True,"data":options}

@app.get("/subscriptiondata/{user_id}")
def getSubscriptionData(user_id:str):
    with open("assets/subscription_data.json", 'r') as file:
        data = json.load(file)
    for i in data:
        if(i["user_id"]==user_id):
            return {"result":True,"data":i}
    else:
        return {"result":False,"data":"No Subscription Data Found !"}

class SubscriptionModel(BaseModel):
    topic:str
    subtopic:str
    user_id:str

@app.post("/addSubscription")
def addSubscription(subdata:SubscriptionModel):
    with open("assets/subscription_data.json", 'r') as file:
        data = json.load(file)
    for user in data:
        print(user)
        if(user["user_id"]==subdata.user_id):
            if(subdata.topic in user["subscription_data"]):
                if(subdata.subtopic not in user["subscription_data"][subdata.topic]["sub_topic"]):
                    user["subscription_data"][subdata.topic]["sub_topic"].append(subdata.subtopic)
                    with open("assets/subscription_data.json", 'w') as file:
                        json.dump(data, file, indent=4)
                return {"result":True,"data":"Subscription added Successfully"}
            else:
                user["subscription_data"][subdata.topic]={}
                user["subscription_data"][subdata.topic]["sub_topic"]=[]
                if(subdata.subtopic not in user["subscription_data"][subdata.topic]["sub_topic"]):
                    user["subscription_data"][subdata.topic]["sub_topic"].append(subdata.subtopic)
                with open("assets/subscription_data.json", 'w') as file:
                    json.dump(data, file, indent=4)
                return {"result":True,"data":"Subscription added Successfully"}

    else:
        data1={}
        data1["user_id"]=subdata.user_id
        data1["subscription_data"]={}
        data1["subscription_data"][subdata.topic]={}
        data1["subscription_data"][subdata.topic]["sub_topic"]=[]
        data1["subscription_data"][subdata.topic]["sub_topic"].append(subdata.subtopic)
        data.append(data1)
        with open("assets/subscription_data.json", 'w') as file:
            json.dump(data, file, indent=4)
        return {"result":True,"data":"Subscription added Successfully"}

@app.get("/oldNotifications/{user_id}")
def oldNotifications(user_id:str):
    with open("assets/notifications.json", 'r') as file:
        notification_data = json.load(file)
    for user in notification_data:
        if(user["user_id"]==user_id):
            return {"result":True,"data":user["messages"]}
    return {"result":False,"data":"No new notifications found !"}

@app.post("/markallread/{user_id}")
def MarkAllRead(user_id:str):
    with open("assets/notifications.json", 'r') as file:
        notification_data = json.load(file)
    for user in notification_data:
        if(user["user_id"]==user_id):
            notification_data.remove(user)
            with open("assets/notifications.json", 'w') as file:
                json.dump(notification_data, file, indent=4)
    return {"result":True,"data":"Marked all as read"}


@app.post("/sns/notification")
async def receive_sns_notification(request: Request):
    headers = request.headers
    message_type = headers.get("X-Amz-Sns-Message-Type")

    if message_type == "SubscriptionConfirmation":
        # Extract the SubscribeURL from the request body
        body = await request.body()
        data = json.loads(body)
        subscribe_url = data.get("SubscribeURL")
        if subscribe_url:
            RedirectResponse(url=subscribe_url)
            return {"SubscribeURL": subscribe_url}
        else:
            raise HTTPException(status_code=400, detail="SubscribeURL not found in the request")
    elif message_type == "Notification":
        # Handle notification message
        body = await request.body()
        data = json.loads(body)
        return {"message": data}
    else:
        raise HTTPException(status_code=400, detail="Invalid message type")

@app.post("/sns/filteredData")
async def getFilteredData(data:SportsUpdatesNotification):
    print(data)
    print(manager.active_connections)
    with open("assets/subscription_data.json", 'r') as file:
        subscription_data = json.load(file)
    for connection in manager.active_connections:
        print("checking connection : ", connection)
        for s_data in subscription_data:
            if(s_data["user_id"]==connection):
                print("subscription data for user ",s_data["user_id"],s_data)
                keys=(data.body.Subject).split(":")
                final_notification={
                "Message_id":data.body.MessageId,
                "Topic":keys[0],
                "Sub_topic":keys[1],
                "Message":data.body.Message,
                "Date":data.body.Timestamp
                }
                if(len(keys)==1):
                    if(keys[0] in s_data["subscription_data"] and len(s_data["subscription_data"][keys[0]]["sub_topic"])==0):
                        await manager.active_connections[connection].send_json(final_notification)
                else:
                    if(keys[0] in s_data["subscription_data"] and (keys[1] in s_data["subscription_data"][keys[0]]["sub_topic"])):
                        await manager.active_connections[connection].send_json(final_notification)
    for s_data in subscription_data:
        found=False
        for connection in manager.active_connections:
                if(s_data["user_id"]==connection):
                    found=True
        if(found==False):
            print("subscription data for inactive user ",s_data["user_id"],s_data)
            notidata={
                "Message_id":"",
                "Topic":"",
                "Sub_topic":"",
                "Message":"",
                "Date":""
            }
            keys=(data.body.Subject).split(":")
            print("keys in inactive ",keys)
            if(len(keys)==1):
                notidata["Topic"]=keys[0]
                keys.append("General")
                notidata["Sub_topic"]=keys[1]
            else:
                notidata["Topic"]=keys[0]
                notidata["Sub_topic"]=keys[1]
            if((keys[0] in s_data["subscription_data"] and len(s_data["subscription_data"][keys[0]]["sub_topic"])==0) or
               (keys[0] in s_data["subscription_data"] and (keys[1] in s_data["subscription_data"][keys[0]]["sub_topic"]))):
                with open("assets/notifications.json", 'r') as file:
                        notification_data = json.load(file)
                for user in notification_data:
                    if(user["user_id"]==s_data["user_id"]):
                        notidata["Date"]=data.body.Timestamp
                        notidata["Message"]=data.body.Message
                        notidata["Message_id"]=data.body.MessageId
                        user["messages"].append(notidata)
                        with open("assets/notifications.json", 'w') as file:
                            json.dump(notification_data, file, indent=4)
                        break
                else:
                    notidata["Date"]=data.body.Timestamp
                    notidata["Message"]=data.body.Message
                    notidata["Message_id"]=data.body.MessageId
                    notidata1={}
                    notidata1["user_id"]=s_data["user_id"]
                    notidata1["messages"]=[]
                    notidata1["messages"].append(notidata)
                    notification_data.append(notidata1)
                    with open("assets/notifications.json", 'w') as file:
                        json.dump(notification_data, file, indent=4) 
    return data

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket,user_id:str):
    await manager.connect(websocket,user_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket,user_id)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
