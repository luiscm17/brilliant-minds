import asyncio
import importlib
import sys

import pytest
from pytest import MonkeyPatch


def _reload_module(module_name: str) -> None:
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.import_module(module_name)


@pytest.fixture
def auth_service(monkeypatch: MonkeyPatch, tmp_path):
    monkeypatch.setenv("AUTH_DB_PATH", str(tmp_path / "users.db"))
    for module in ("src.config.settings", "src.services.auth_service"):
        _reload_module(module)
    import src.services.auth_service as auth_service_module  # noqa: F401

    yield auth_service_module
    for module in ("src.config.settings", "src.services.auth_service"):
        if module in sys.modules:
            del sys.modules[module]


def _run(coro):
    return asyncio.run(coro)


def test_register_and_login(auth_service):
    from src.models.schemas.auth import UserCreate, UserLogin

    payload = UserCreate(
        email="user@example.com", password="password123", name="Tester"
    )
    created = _run(auth_service.register_user(payload))
    assert created.user.email == payload.email.lower()

    login = _run(
        auth_service.login_user(
            UserLogin(email=payload.email, password=payload.password)
        )
    )
    assert login.user.user_id == created.user.user_id


def test_duplicate_email_rejected(auth_service):
    from src.models.schemas.auth import UserCreate
    from src.core.exceptions import EmailAlreadyExistsError

    payload = UserCreate(
        email="user@example.com", password="password123", name="Tester"
    )
    _run(auth_service.register_user(payload))
    with pytest.raises(EmailAlreadyExistsError):
        _run(auth_service.register_user(payload))


def test_login_with_wrong_password(auth_service):
    from src.models.schemas.auth import UserCreate, UserLogin
    from src.core.exceptions import InvalidCredentialsError

    payload = UserCreate(
        email="user@example.com", password="password123", name="Tester"
    )
    _run(auth_service.register_user(payload))
    with pytest.raises(InvalidCredentialsError):
        _run(
            auth_service.login_user(UserLogin(email=payload.email, password="bad-pass"))
        )
