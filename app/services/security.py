from fastapi import Header, HTTPException, status, Depends
from app.config import API_KEY

def verify_api_key(authorization: str = Header(...)):
    """
    Verifies the API key from the Authorization header.
    Expected format: 'Bearer <API_KEY>'
    """
    try:
        scheme, key = authorization.split()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    if scheme.lower() != "bearer" or key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    
    return True

# Dependency you can inject in routes
ApiKeyDep = Depends(verify_api_key)