from fastapi import FastAPI
from routers import tasks, users
from dotenv import load_dotenv
from db.databaseConnect import connectToDatabase, disconnectFromDatabase

# Load environment variables from .env file
load_dotenv()

app:FastAPI = FastAPI()

@app.get('/')
async def root():
    return {"message": "hi"}

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