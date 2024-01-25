from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, Depends, status
from utils.accessTokenUtils import getAccessTokenData
from models.taskModel import CreateTask, UpdateTask
from datetime import datetime

# Checking if the task ID is valid
def checkObjectId(objectId):
    if(ObjectId.is_valid(objectId)):
        return True
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Task ID is not valid."})
    

# Tasks Router
router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(getAccessTokenData)] )

# Get Tasks
@router.get("/get", status_code=status.HTTP_200_OK)
async def getTasks(request: Request, status: str = None, accessTokenData: dict = Depends(getAccessTokenData)):
    try:
        # Setting up the query filters
        tasksFilters:dict = {}
        
        if(status in ["Not Started","In Progress", "Completed"]):
            tasksFilters["status"] = status
            
        role = accessTokenData.get('role')
        if role == "user":
            tasksFilters["user_id"] = accessTokenData.get("id")

        # Getting the tasks by the filters
        tasks=list(request.app.database["tasks"].find(tasksFilters,{"_id":0}))
        return tasks 
   
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})


# Add a Task
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def addTask(request: Request, task: CreateTask, accessTokenData: dict = Depends(getAccessTokenData)):
    try:
        # Default task properties
        task.status = "Not Started"
        task.created_at = datetime.utcnow()
        
        role = accessTokenData["role"]
        tokenUserId = accessTokenData.get("id")
        successMessage = "Task created for"

        # Checking what User ID to use for the task
        if role == "admin":
            if(task.user_id != None):
                # Checking if the user exists
                result = request.app.database["users"].find_one({"_id": task.user_id})
                if(result == None):
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": "User not found"})
                
                successMessage += " a user"
            else:               
                task.user_id = tokenUserId
                successMessage += " the admin"   
        else:
            successMessage += " the user"
            task.user_id = tokenUserId
            
        # Saving the task
        request.app.database["tasks"].insert_one(task.model_dump())
        
        return {"Message": successMessage}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
    
# Delete a task
@router.delete("/delete")
async def deleteTask(request:Request, taskId:str, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Checking if the task ID is valid
        checkObjectId(taskId)
        
        # Deleting the task
        userId = accessTokenData.get("id")
        result = request.app.database["tasks"].delete_one({"_id":ObjectId(taskId), "user_id":userId})
        
        # Checking if the task has been deleted
        if(result.deleted_count == 0):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"Task not found"})
        
        return {"Message":"Task deleted successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Delete all completed tasks
@router.delete("/delete-completed")
async def deleteCompletedTask(request:Request, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Deleting all completed tasks
        userId = accessTokenData.get("id")
        result = request.app.database["tasks"].delete_many({"user_id":userId, "status":"Completed"})
        
        # Checking if any completed tasks has been deleted
        if(result.deleted_count == 0):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"Didn't find any tasks"})
        
        return {"Message":"Completed tasks deleted successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Update a task 
@router.patch("/update")
async def updateTask(request:Request, task:UpdateTask, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Checking if the task ID is valid
        checkObjectId(task.task_id)
        
        userId = accessTokenData.get("id") 
        valuesToUpdate: dict = {}
        
        # Setting up the values to update in the task
        if(task.message != None):
            valuesToUpdate["message"] = task.message
        if(task.status != None):
            valuesToUpdate["status"] = task.status
            
        # Updating the task with the new values
        result = request.app.database["tasks"].update_one({"_id":ObjectId(task.task_id), "user_id":userId}, {"$set":  valuesToUpdate})
        
        # Checking if a task was successfully updated
        if(result.matched_count == 0):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"Task not found"})
        return {"Message":"Task updated successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
    
    

