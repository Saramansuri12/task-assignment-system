import os
import asyncio

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_api.db")

import httpx

from app.main import app


async def request(method, path, **kwargs):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, **kwargs)


def test_root_endpoint_is_available():
    response = asyncio.run(request("GET", "/"))

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_register_and_login_round_trip():
    username = "integration_test_user"
    password = "integration-test-password"

    register_response = asyncio.run(request(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "email": "integration@example.com",
            "password": password,
            "role": "EMPLOYEE",
        },
    ))

    assert register_response.status_code in (201, 409)

    login_response = asyncio.run(request(
        "POST",
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    ))

    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert login_response.json()["access_token"]