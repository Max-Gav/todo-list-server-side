from pydantic import BaseModel, EmailStr, constr, Field
from typing import Literal
from datetime import datetime

# User Creation Model
class CreateUser(BaseModel):
    username: constr(min_length=3, max_length=20)
    email: EmailStr = Field(...)
    password: str

    
# User Login Model
class LoginUser(BaseModel):
    email: str
    password: str



 



