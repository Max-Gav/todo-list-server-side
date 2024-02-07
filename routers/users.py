from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Response, status, Depends
from models.userModel import CreateUser, LoginUser
from utils.passwordUtils import comparePassword, encryptPassword
from utils.accessTokenUtils import setAccessTokenInResponse, createToken, getAccessToken, getAccessTokenData

# Users Router
router = APIRouter(prefix="/users", tags=["users"])

# Create and store an access Token
def setAccessToken(userId: str, userRole: str, request: Request, response: Response):
    accessToken = createToken(userId=userId, userRole=userRole)
    setAccessTokenInResponse(token=accessToken, request=request, response=response)

# Get Users
@router.get("/get", status_code=status.HTTP_200_OK)
async def getUsers(request: Request):
   users=list(request.app.database["users"].find({},{"username":1,"_id":0}))
   return users

# Sign Up User
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def createUser(request: Request, response: Response, userDetails: CreateUser):
    try:
        # User properties
        user:dict = {}
        user["username"] = userDetails.username
        user["email"] = userDetails.email
        user["role"] = "user"
        user["password"] = encryptPassword(userDetails.password)
        user["created_at"] = datetime.utcnow()
        
        # Creating a new user
        newUser=request.app.database["users"].insert_one(user)
        
        setAccessToken(userId=str(newUser.inserted_id), userRole=user["role"], request=request, response=response)
        return {"Message":"Created a user"}
    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        if hasattr(error, 'code') and error.code == 11000:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"Error":"User's email already exists"})
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Login User
@router.post("/login", status_code=status.HTTP_200_OK)
async def loginUser(request: Request, response: Response, user: LoginUser):
    try:
        # Finding the user in the database
        currUser=request.app.database["users"].find_one({"email":user.email})
        
        # Checking if login was successful
        if(currUser is None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error":"No matching email"})
        if(comparePassword(user.password, currUser["password"]) == False):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Error":"Incorrect Password"})
        setAccessToken(userId=str(currUser.get("_id")), userRole=currUser.get("role"), request=request, response=response)
        return {"Message":"User logged in", "role": currUser.get("role")}
    except HTTPException as error:
        raise error
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Check if User is Logged in
@router.get("/is-logged-in", status_code=status.HTTP_200_OK)
async def isLoggedIn(request: Request, accessTokenData:dict = Depends(getAccessTokenData)):
    try:
        if(accessTokenData == None):
            return {"Message":"User is not logged in", "answer":False}
        return {"Message":"User logged in", "answer":True, "role": accessTokenData["role"]}
    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})


# Logout User
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logoutUser(response: Response):
    try:
        response.delete_cookie("access-token", secure=True, samesite='none')
        return {"Message":"User logged out"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})


        
        

