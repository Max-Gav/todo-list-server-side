from fastapi import FastAPI, Depends, HTTPException, status
from routers import tasks, users
from dotenv import load_dotenv
from db.databaseConnect import connectToDatabase, disconnectFromDatabase
from utils.accessTokenUtils import getAccessTokenData
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

app:FastAPI = FastAPI()

# Setting up cors middleware
origins = [
    "http://localhost:5174","http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Client-Type"],
)

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