from fastapi import HTTPException, status
import bcrypt

# Encrypt a password using hash
def encryptPassword(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed_password.decode('utf-8')

# Check if the provided password matches the hashed password
def comparePassword(password: str, hashedPassword: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashedPassword.encode('utf-8'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Error":"Internal Server Error"})
