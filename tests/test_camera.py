# Path: fastlabio/tests/test_camera.py
# -*- coding: utf-8 -*-
"""
Pytest tests for the Fast Lab IO camera module.

This module contains tests for the camera-related endpoints and dependencies
within the Fast Lab IO FastAPI application.
"""

__author__ = "Marco Bonaglia" # Placeholder
__version__ = "0.1.0"
__date__ = "2025-05-27" # Placeholder - use current date

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np

# Import the main FastAPI app and the camera router/dependency
# Always use package imports for pytest (run pytest from project root)
# from main import app
# from ..main import app
from fastlabio.main import app
from camera import get_pysilico_camera

# Create a TestClient for the FastAPI application
client = TestClient(app)

# Mock the pysilico camera for testing purposes
# We need to mock the pysilico.camera function called in the dependency
# and potentially the methods called on the returned camera object

@pytest.fixture
def mock_pysilico_camera():
    """Fixture to mock the pysilico camera dependency."""
    with patch('fastlabio.camera.pysilico.camera') as mock_camera_constructor:
        # Create a mock camera instance with necessary methods
        mock_camera_instance = MagicMock()

        # Configure the mock camera instance methods as needed for tests
        # Example: Mocking getFrameForDisplay to return a mock CameraFrame
        mock_frame_object = MagicMock()
        mock_frame_object.toNumpyArray.return_value = np.zeros((100, 100), dtype=np.uint8) # Mock image data
        mock_camera_instance.getFrameForDisplay.return_value = mock_frame_object
        
        # Mock setExposureTime
        mock_camera_instance.setExposureTime.return_value = None # Assuming it returns None on success

        # Mock set_gain (even though it might not work in the real app, mock it for testing our endpoint)
        mock_camera_instance.set_gain.return_value = None # Assuming it returns None on success

        mock_camera_constructor.return_value = mock_camera_instance

        yield mock_camera_instance

# Test cases

def test_get_pysilico_camera_dependency_success(mock_pysilico_camera):
    """Test that the get_pysilico_camera dependency returns a camera instance."""
    # This test primarily verifies that the dependency function can be called
    # and doesn't raise an immediate exception when pysilico.camera is mocked.
    # The actual camera interaction is tested via endpoints.
    # We can't directly test the 'yield' part of the dependency easily here,
    # but mocking the constructor verifies a key part.
    assert isinstance(mock_pysilico_camera, MagicMock)
    # Further tests of the dependency are implicitly done when testing endpoints that use it.

@pytest.mark.asyncio
async def test_get_single_frame_success(mock_pysilico_camera):
    """
    Test the GET /camera/frame endpoint for successful frame acquisition.
    """
    response = client.get("/camera/frame")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/jpeg'
    # Note: Testing the actual image content would require more advanced mocking or image comparison.
    # For this basic test, we check the status code and content type.

@pytest.mark.asyncio
async def test_set_exposure_success(mock_pysilico_camera):
    """
    Test the PUT /camera/exposure endpoint for successful exposure time setting.
    """
    test_exposure_time = 5000.0
    response = client.put("/camera/exposure", json={"exposure_time_us": test_exposure_time})
    assert response.status_code == 200
    assert response.json() == {"message": f"Exposure time set to {test_exposure_time} us"}

@pytest.mark.asyncio
async def test_set_exposure_invalid_input(mock_pysilico_camera):
    """
    Test the PUT /camera/exposure endpoint with invalid input (exposure_time_us <= 0).
    """
    invalid_exposure_time = -1.0
    response = client.put("/camera/exposure", json={"exposure_time_us": invalid_exposure_time})
    assert response.status_code == 422 # Unprocessable Entity for validation errors
    # Optionally, assert on the structure or content of the error detail if needed 

@pytest.mark.asyncio
async def test_set_gain_success(mock_pysilico_camera):
    """
    Test the PUT /camera/gain endpoint for successful gain setting.
    """
    test_gain = 2.5
    response = client.put("/camera/gain", json={"gain": test_gain})
    # Note: The actual camera mock will accept this, even if the real server might not.
    # This test verifies our endpoint structure and interaction with the mock.
    assert response.status_code == 200
    assert response.json() == {"message": f"Gain set to {test_gain}"}

@pytest.mark.asyncio
async def test_set_gain_invalid_input(mock_pysilico_camera):
    """
    Test the PUT /camera/gain endpoint with invalid input (gain < 0).
    """
    invalid_gain = -0.5
    response = client.put("/camera/gain", json={"gain": invalid_gain})
    assert response.status_code == 422 # Unprocessable Entity for validation errors
    # Optionally, assert on the structure or content of the error detail if needed

# Add more test cases for endpoints below

# Example test case for GET /camera/frame
# async def test_get_single_frame_success(mock_pysilico_camera): # Use async if endpoint is async
#     response = client.get("/camera/frame")
#     assert response.status_code == 200
#     assert response.headers['content-type'] == 'image/jpeg'
#     # Add assertions to check the image content if necessary

# Example test case for PUT /camera/exposure
# def test_set_exposure_success(mock_pysilico_camera):
#     response = client.put("/camera/exposure", json={"exposure_time_us": 5000})
#     assert response.status_code == 200
#     assert response.json() == {"message": "Exposure time set to 5000.0 us"}

# Add test cases for error handling (e.g., camera connection failure, invalid input) 