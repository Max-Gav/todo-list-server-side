from pydantic import BaseModel, constr
from typing import Literal

# Task Model
class CreateTask(BaseModel):
    message: constr(min_length=1, max_length=200)
    
class UpdateTask(BaseModel):
    task_id: str
    message: constr(min_length=1, max_length=200) = None
    status: Literal["Not Started","In Progress", "Completed"] = None




 



