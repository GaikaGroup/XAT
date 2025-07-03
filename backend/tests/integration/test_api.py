import pytest
from app.main import app


def test_chat_endpoint():
    # Crear un cliente de prueba
    client = app.test_client()

    # Datos de entrada
    payload = {"message": "Hola"}

    # Realizar la solicitud POST al endpoint
    response = client.post("/chat", json=payload)

    # Verificar el código de estado y la respuesta
    assert response.status_code == 200
    assert "response" in response.json
