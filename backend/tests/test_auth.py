"""Authentication tests."""

from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json={
        "phone_number": "+254712345678",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "location": "Nairobi",
        "password": "securepassword123"
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["phone_number"] == "+254712345678"


def test_login_user(client):
    """Test user login."""
    # Register user first
    client.post("/api/v1/auth/register", json={
        "phone_number": "+254712345678",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "location": "Nairobi",
        "password": "securepassword123"
    })

    # Login
    response = client.post("/api/v1/auth/login", json={
        "phone_number": "+254712345678",
        "password": "securepassword123"
    })

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
