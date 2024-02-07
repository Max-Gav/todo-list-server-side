from pydantic import BaseModel, constr, EmailStr
from typing import Literal

# Task Models
class CreateTask(BaseModel):
    message: constr(min_length=1, max_length=200)
    userEmail: EmailStr = None
    
class UpdateTask(BaseModel):
    taskId: str
    message: constr(min_length=1, max_length=200) = None
    status: Literal["Not Started","In Progress", "Completed"] = None
    
class TaskDetails(BaseModel):
    taskId: str = None
    





 



