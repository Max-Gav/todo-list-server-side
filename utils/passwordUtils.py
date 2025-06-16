from fastapi import HTTPException, status
from decouple import config
import bcrypt
import base64

# .env variables
PEPPER_SECRET = config("PEPPER_SECRET")

# Check if password is valid
def isValidPassword(password):
    return len(password) >= 8 and len(password) <= 20
    
# Decode password from base64
def decodePasswordFromBase64(password):
    try:
        return base64.b64decode(password).decode('utf-8')
    except base64.binascii.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Password is not using the right base64 encoding"})

# Encrypt a password using hash
def encryptPassword(password: str) -> str:
    try:
        decodedPassword = decodePasswordFromBase64(password)
        if(isValidPassword(decodedPassword)):
            # Adding salt and pepper to the password
            pepperedPassword = decodedPassword + PEPPER_SECRET
            salt = bcrypt.gensalt()
            hashedPassword = bcrypt.hashpw(pepperedPassword.encode('utf-8'), salt)
            
            return hashedPassword.decode('utf-8')
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error": "Invalid password"})

    except HTTPException as error:
        print(error)
        raise error 
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})



# Check if the provided password matches the hashed password
def comparePassword(password: str, hashedPassword: str) -> bool:
    try:
        decodedPassword = decodePasswordFromBase64(password)
        pepperedPassword = decodedPassword + PEPPER_SECRET

        return bcrypt.checkpw(pepperedPassword.encode('utf-8'), hashedPassword.encode('utf-8'))
    except HTTPException as error:
        raise error 
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
