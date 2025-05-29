# Path: fastlabio/tests/test_motor.py
# -*- coding: utf-8 -*-
"""
Pytest tests for the Fast Lab IO motor module.

This module contains tests for the motor-related endpoints and dependencies
within the Fast Lab IO FastAPI application.
"""

__author__ = "Your Name/Team" # Placeholder
__version__ = "0.1.0"
__date__ = "2023-10-27" # Placeholder - use current date

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the main FastAPI app and the camera router/dependency
# Always use package imports for pytest (run pytest from project root)
# from main import app
# from ..main import app
from fastlabio.fastlabio.main import app
from fastlabio.fastlabio.motor import get_plico_motor, MotorMoveRequest, MotorSpeedRequest

# Create a TestClient for the FastAPI application
client = TestClient(app)

# Mock the plico_motor client for testing purposes
# We need to mock the client instantiation and the methods called on the client object

@pytest.fixture
def mock_plico_motor_client():
    """Fixture to mock the plico_motor client dependency."""
    # Patch the specific client class or function used in get_plico_motor
    # Adjust 'plico.motor.motor_client' based on the actual import/usage in fastlabio/motor.py
    with patch('plico_motor.motor') as mock_motor_constructor:
        # Create a mock motor instance with necessary methods
        mock_motor_instance = MagicMock()

        # Configure the mock motor instance methods as needed for tests
        mock_motor_instance.move = MagicMock(return_value=None) # Mock move method
        mock_motor_instance.get_position = MagicMock(return_value=10.0) # Mock get_position method, return a sample position
        mock_motor_instance.set_speed = MagicMock(return_value=None) # Mock set_speed method
        mock_motor_instance.close = MagicMock(return_value=None) # Mock close method

        mock_motor_constructor.return_value = mock_motor_instance

        yield mock_motor_instance

# Test cases for motor endpoints will be added below 

@pytest.mark.asyncio
async def test_move_motor_success(mock_plico_motor_client):
    """
    Test the PUT /motor/move endpoint for a successful move command.
    """
    target_position = 50.0
    response = client.put("/motor/move", json={"position": target_position})

    assert response.status_code == 200
    assert response.json() == {"message": f"Motor moving to position: {target_position}"}
    # Verify that the mock move method was called with the correct position
    mock_plico_motor_client.move.assert_called_once_with(target_position)

@pytest.mark.asyncio
async def test_move_motor_invalid_input():
    """
    Test the PUT /motor/move endpoint with invalid input.
    """
    # Assuming position must be a number
    response = client.put("/motor/move", json={"position": "invalid_position"})

    assert response.status_code == 422 # FastAPI returns 422 for validation errors
    assert "validation error" in response.json()["detail"][0]["msg"].lower() # Check for validation error message

@pytest.mark.asyncio
async def test_get_motor_position_success(mock_plico_motor_client):
    """
    Test the GET /motor/position endpoint for a successful position retrieval.
    """
    expected_position = 10.0 # This matches the return_value in the mock fixture
    response = client.get("/motor/position")

    assert response.status_code == 200
    assert response.json() == {"position": expected_position}
    # Verify that the mock get_position method was called
    mock_plico_motor_client.get_position.assert_called_once()

@pytest.mark.asyncio
async def test_set_motor_speed_success(mock_plico_motor_client):
    """
    Test the PUT /motor/speed endpoint for a successful speed setting.
    """
    target_speed = 100.0
    response = client.put("/motor/speed", json={"speed": target_speed})

    assert response.status_code == 200
    assert response.json() == {"message": f"Motor speed set to: {target_speed}"}
    # Verify that the mock set_speed method was called with the correct speed
    mock_plico_motor_client.set_speed.assert_called_once_with(target_speed)

@pytest.mark.asyncio
async def test_set_motor_speed_invalid_input():
    """
    Test the PUT /motor/speed endpoint with invalid input.
    """
    # Assuming speed must be a number
    response = client.put("/motor/speed", json={"speed": "invalid_speed"})

    assert response.status_code == 422 # FastAPI returns 422 for validation errors
    assert "validation error" in response.json()["detail"][0]["msg"].lower() # Check for validation error message
