from fastapi import HTTPException, status


class DocSimplifyException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An internal error occurred",
    ):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundError(DocSimplifyException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class EmailAlreadyExistsError(DocSimplifyException):
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InvalidCredentialsError(DocSimplifyException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UnauthorizedError(DocSimplifyException):
    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
