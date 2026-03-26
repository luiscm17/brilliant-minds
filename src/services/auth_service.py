import uuid
from src.core.security import create_access_token


async def register_user(body):
    """Placeholder for user registration connection point."""
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id)
    return {
        "token": token,
        "userId": user_id,
        "user": {"userId": user_id, "email": body.email, "name": body.name},
    }


async def login_user(body):
    """Placeholder for user login connection point."""
    user_id = "mock-user-id"
    token = create_access_token(user_id)
    return {
        "token": token,
        "userId": user_id,
        "user": {"userId": user_id, "email": body.email, "name": "User Mock"},
    }
