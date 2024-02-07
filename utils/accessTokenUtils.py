import time
from fastapi import HTTPException, Request, Response, status
from decouple import config
import jwt

# .env variables
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_SECRET = config("JWT_SECRET")

# Create a new token
def createToken(userId: str, userRole: str) -> str:
    payload = {
        "id": userId,
        "role": userRole,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# Decode an access token
def decodeAccessToken(token: str):
    try:
        decodedToken = jwt.decode(token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decodedToken
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Error": "Invalid Access token"})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
    
# Get the access token according to the client type
def getAccessToken(request: Request):
        clientType = request.headers.get('Client-Type')
        accessToken = None

        # Get the access token according to the user agent
        if clientType == "web":
            accessToken = request.cookies.get('access-token')
        elif clientType == "mobile":
            # TODO: Return the access token from the headers for mobile users
            pass
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Invalid or no Client-Type header"})

        return accessToken
    
# Return the access token data
def getAccessTokenData(request: Request):
    try:   
        accessToken = getAccessToken(request)
        
        # Check if an access token was found
        if accessToken == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Error": "Access token not found"})
        
        # Decoding the access token and returning it
        decodedAccessToken = decodeAccessToken(accessToken)
        return decodedAccessToken
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})

# Set the user's access token in the response
def setAccessTokenInResponse(request:Request,response: Response, token: str):
    clientType = request.headers.get('Client-Type', default=None)
    print(clientType)

    # Checking the source of the request
    if clientType == "web":
        response.set_cookie('access-token', token, max_age=6000, httponly=True, secure=True, samesite='none')
    elif clientType == "mobile":
        pass
        # TODO: Save the access token for mobile users
    elif clientType == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "No client type specified"})
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Invalid client type specified"})

