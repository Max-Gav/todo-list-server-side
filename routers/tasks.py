from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, Depends, status
from utils.accessTokenUtils import getAccessTokenData
from models.taskModel import CreateTask, UpdateTask, TaskDetails
from datetime import datetime

# Checking if the task ID is valid
def checkObjectId(objectId):
    if(ObjectId.is_valid(objectId)):
        return True
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Task ID is not valid."})

# Get the username using the user id
def getUsername(request, userId):
    user = request.app.database["users"].find_one({"_id": ObjectId(userId)}, {"username":1})
    return user.get("username")
    

# Tasks Router
router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(getAccessTokenData)] )

# Get Tasks
@router.get("/get", status_code=status.HTTP_200_OK)
async def getTasks(request: Request, accessTokenData: dict = Depends(getAccessTokenData)):
    try:
        # Setting up the query filters
        taskFilters:dict = {}
        
        # Checking the client type
        clientType = request.headers.get('Client-Type')
    
        # Checking the client role
        role = accessTokenData.get('role')
        if role == "user" or clientType == "mobile":
            taskFilters["user_id"] = accessTokenData.get("id")

        # Getting the tasks by the filters
        tasks=list(request.app.database["tasks"].find(taskFilters))
        for task in tasks:
            task["_id"] = str(task.get("_id"))
            task["username"] = getUsername(request, task.get("user_id"))
        return tasks
   
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})


# Add a Task
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def addTask(request: Request, taskPayload:CreateTask, accessTokenData: dict = Depends(getAccessTokenData)):
    try:
        # Success message string
        successMessage = "Task created for"

        # Task properties
        task:dict = {}
        task["message"] = taskPayload.message
        task["status"] = "Not Started"
        task["created_at"] = datetime.utcnow()
        
        # Getting access token data
        role = accessTokenData.get("role")
        userId = accessTokenData.get("id")
        
        # Checking what User ID to use for the task
        if role == "admin":
            if(taskPayload.userEmail != None):
                # Checking if the user exists
                user = request.app.database["users"].find_one({"email": taskPayload.userEmail})
                if(user == None):
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": "User not found"})
                
                userId = str(user.get("_id"))
                successMessage += " a user"
            else:               
                successMessage += " the admin"   
        else:
            successMessage += " the user"
            
        task["user_id"] = userId
        
        # Saving the task
        newTask = request.app.database["tasks"].insert_one(task)
        
        # Adding the task ID and username to the task object in order to return
        task["_id"] = str(newTask.inserted_id)
        task["username"] = getUsername(request, userId)

        return {"Message": successMessage, "task":task}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
    
# Delete a task
@router.delete("/delete", status_code=status.HTTP_200_OK)
async def deleteTask(request:Request, taskDetails: TaskDetails, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Checking if the task ID is valid
        checkObjectId(taskDetails.taskId)
        
        # Getting the access token data
        role = accessTokenData.get("role")
        
        if role == "admin":
            result = request.app.database["tasks"].delete_one({"_id":ObjectId(taskDetails.taskId)})
        else:
            tokenUserId = accessTokenData.get("id")
            result = request.app.database["tasks"].delete_one({"_id":ObjectId(taskDetails.taskId), "user_id":tokenUserId})
            
        # Checking if the task has been deleted
        if(result.deleted_count == 0):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"Task not found"})
        
        return {"Message":"Task deleted successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Delete all completed tasks
@router.delete("/delete-completed", status_code=status.HTTP_200_OK)
async def deleteCompletedTask(request:Request, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Deleting all completed tasks
        userId = accessTokenData.get("id")
        role = accessTokenData.get("role")
        
        if role == "admin":
            result = request.app.database["tasks"].delete_one({"status":"Completed"})
        else:
            result = request.app.database["tasks"].delete_one({"user_id":userId, "status":"Completed"})
        
        # Checking if any completed tasks has been deleted
        if(result.deleted_count == 0):
            return {"Message":"Didn't find any tasks"}
        
        return {"Message":"Completed tasks deleted successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Update a task 
@router.patch("/update", status_code=status.HTTP_200_OK)
async def updateTask(request:Request, task:UpdateTask, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        # Checking if the task ID is valid
        checkObjectId(task.taskId)
        
        # Getting access token data
        role = accessTokenData.get("role")
        tokenUserId = accessTokenData.get("id")
        
        # Setting up the values to update in the task
        valuesToUpdate: dict = {}
        
        if(task.message != None):
            valuesToUpdate["message"] = task.message
        if(task.status != None):
            valuesToUpdate["status"] = task.status
            
        # Updating the task with the new values
        if(role == "admin"):
            result = request.app.database["tasks"].update_one({"_id":ObjectId(task.taskId)}, {"$set":  valuesToUpdate})
        else:
            result = request.app.database["tasks"].update_one({"_id":ObjectId(task.taskId), "user_id":tokenUserId}, {"$set":  valuesToUpdate})
            
        
        # Checking if a task was successfully updated
        if(result.matched_count == 0):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"Task not found"})
        return {"Message":"Task updated successfully"}
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
    
# Check if a task is eligible for a notification
@router.post("/notification-eligible", status_code=status.HTTP_200_OK)
async def checkTaskNotification(request:Request, taskDetails: TaskDetails, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        currentUserId = accessTokenData.get("id")
        currentTask = request.app.database["tasks"].find_one({"_id":ObjectId(taskDetails.taskId),"user_id":currentUserId})
        if(currentTask == None or currentTask.get("status") == "Completed"):
            return {"answer": False}
        return {"answer":True, "message": currentTask.get("message")}
   
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

