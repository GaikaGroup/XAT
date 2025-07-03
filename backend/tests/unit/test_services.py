import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pytest
from app.services.chat_service import ChatService


def test_chat_response(mocker):
    # Simula una respuesta de una API externa
    mocker.patch('app.services.chat_service.ChatService.external_api_call', return_value="Hola!")

    response = ChatService.get_response("Hola")

    assert response == "¡Hola! ¿Cómo estás?"
