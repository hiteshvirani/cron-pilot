from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import config
import secrets

security = HTTPBasic()

def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    is_username_correct = secrets.compare_digest(
        credentials.username, config.admin_username
    )
    is_password_correct = secrets.compare_digest(
        credentials.password, config.admin_password
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

def get_current_admin(current_admin: str = Depends(verify_admin_credentials)):
    """Get current admin user"""
    return current_admin 