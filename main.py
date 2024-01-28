from fastapi import FastAPI, Depends, HTTPException, status
from routers import tasks, users
from dotenv import load_dotenv
from db.databaseConnect import connectToDatabase, disconnectFromDatabase
from utils.accessTokenUtils import getAccessTokenData

# Load environment variables from .env file
load_dotenv()

app:FastAPI = FastAPI()

@app.get('/')
async def root():
    return {"message": "hi"}

@app.get("/access-token-data")
async def getAccessTokenData(accessTokenData: dict = Depends(getAccessTokenData)):
    try:
        return {"data": accessTokenData}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Connect/Disconnect from database
@app.on_event("startup")
def startup_db_client():
    connectToDatabase(app)

@app.on_event("shutdown")
def shutdown_db_client():
    disconnectFromDatabase(app)

# Server routes
app.include_router(tasks.router)
app.include_router(users.router)