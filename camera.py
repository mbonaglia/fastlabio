# Path: fastlabio/camera.py
# -*- coding: utf-8 -*-
"""
Camera module for Fast Lab IO.

This module provides the FastAPI router and dependency functions for interacting
with the pysilico camera.
"""

__author__ = "Marco Bonaglia" # Placeholder
__version__ = "0.1.0"
__date__ = "2025-05-27" # Placeholder - use current date

import asyncio
import logging
import cv2
import pysilico
from fastapi import HTTPException, status, APIRouter, Depends, Response, Body, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Set up logging for this module
logger = logging.getLogger(__name__)

# Configuration constants (placeholders)
CAMERA_HOST = "localhost" # Replace with actual camera server IP
CAMERA_PORT = 7100        # Replace with actual camera server port

class ExposureSettings(BaseModel):
    """Pydantic model for camera exposure time settings."""
    exposure_time_us: float = Field(..., gt=0, description="Exposure time in microseconds")

class GainSettings(BaseModel):
    """
Pydantic model for camera gain settings.

Note: Validate gain range based on specific camera capabilities if known.
"""
    gain: float = Field(..., ge=0, description="Camera gain value") # Adjust ge/le based on camera spec

camera_router = APIRouter()

async def get_pysilico_camera():
    """
    FastAPI dependency to get a pysilico camera instance.

    Connects to the pysilico camera server and yields the camera instance.
    Ensures the connection is closed afterwards.
    Handles connection errors by raising HTTPException.
    """
    camera = None
    try:
        # Connect to the camera server, wrapping the blocking call
        logger.info(f"Attempting to connect to camera at {CAMERA_HOST}:{CAMERA_PORT}")
        camera = await asyncio.to_thread(pysilico.camera, CAMERA_HOST, CAMERA_PORT)
        logger.info("Camera connection successful.")
        yield camera
    except Exception as e:
        logger.error(f"Error connecting to camera: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not connect to camera: {e}"
        )
    finally:
        if camera:
            logger.info("Closing camera connection.")
            # Assuming pysilico camera object has a close or similar method if needed
            # await asyncio.to_thread(camera.close) # Uncomment if a close method exists

# Future camera endpoints will be added here using a APIRouter
# from fastapi import APIRouter
# camera_router = APIRouter()

@camera_router.get("/frame")
async def get_single_frame(camera: pysilico.camera = Depends(get_pysilico_camera)):
    """
    Acquire a single frame from the camera.

    Returns the image frame as a JPEG byte stream.
    Raises HTTPException on errors during frame acquisition or encoding.
    """
    try:
        logger.info("Acquiring single frame from camera.")
        # Assuming getFutureFrames returns a list of frames, take the first one
        frame_object = await asyncio.to_thread(camera.getFrameForDisplay, 1)
        if not frame_object:
            logger.error("No frames received from camera.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No frames received from camera"
            )

        frame = frame_object.toNumpyArray()

        # Encode the frame to JPEG format
        logger.info("Encoding frame to JPEG.")
        # Assuming frame is a NumPy array compatible with cv2.imencode
        is_success, buffer = cv2.imencode(".jpg", frame)

        if not is_success:
            logger.error("Could not encode frame to JPEG.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not encode frame to JPEG"
            )

        # Convert buffer to bytes
        jpeg_bytes = buffer.tobytes()

        logger.info("Single frame acquired and encoded successfully.")
        return Response(content=jpeg_bytes, media_type="image/jpeg")

    except Exception as e:
        logger.error(f"Error acquiring or encoding frame: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acquiring or encoding frame: {e}"
        )

@camera_router.put("/exposure")
async def set_exposure(settings: ExposureSettings = Body(...), camera: pysilico.camera = Depends(get_pysilico_camera)):
    """
    Set the camera exposure time.

    Args:
        settings: Exposure settings including the desired exposure time in microseconds.
        camera: The pysilico camera instance provided by the dependency.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If there is an error setting the exposure time.
    """
    try:
        logger.info(f"Attempting to set exposure time to {settings.exposure_time_us} us.")
        await asyncio.to_thread(camera.setExposureTime, settings.exposure_time_us)
        logger.info("Exposure time set successfully.")
        return {"message": f"Exposure time set to {settings.exposure_time_us} us"}
    except Exception as e:
        logger.error(f"Error setting exposure time: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not set exposure time: {e}"
        )

@camera_router.put("/gain")
async def set_gain(settings: GainSettings = Body(...), camera: pysilico.camera = Depends(get_pysilico_camera)):
    """
    Set the camera gain.

    Args:
        settings: Gain settings including the desired gain value.
        camera: The pysilico camera instance provided by the dependency.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If there is an error setting the gain.
    """
    try:
        logger.info(f"Attempting to set gain to {settings.gain}.")
        # Assuming pysilico camera has a set_gain method
        await asyncio.to_thread(camera.set_gain, settings.gain)
        logger.info("Gain set successfully.")
        return {"message": f"Gain set to {settings.gain}"}
    except Exception as e:
        logger.error(f"Error setting gain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not set gain: {e}"
        )

@camera_router.websocket("/ws/camera/stream")
async def websocket_camera_stream(websocket: WebSocket, camera: pysilico.camera = Depends(get_pysilico_camera)):
    """
    WebSocket endpoint for streaming real-time camera frames.

    Accepts a WebSocket connection and continuously sends JPEG encoded frames.
    Handles client disconnection and errors during streaming.

    Args:
        websocket: The WebSocket object for communication.
        camera: The pysilico camera instance provided by the dependency.
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted for camera stream.")

    try:
        while True:
            try:
                # Acquire a single frame
                frames = await asyncio.to_thread(camera.getFutureFrames, 1)
                if not frames:
                    logger.warning("No frames received in WebSocket stream loop.")
                    continue

                frame = frames[0]

                # Encode the frame to JPEG format
                is_success, buffer = cv2.imencode(".jpg", frame)
                if not is_success:
                    logger.error("Could not encode frame to JPEG in WebSocket stream.")
                    # Optionally send an error message to the client or close the connection
                    continue # Skip sending this frame but keep connection open

                # Convert buffer to bytes and send over WebSocket
                jpeg_bytes = buffer.tobytes()
                await websocket.send_bytes(jpeg_bytes)

                # Add a small delay to control stream rate, if necessary
                # await asyncio.sleep(0.03) # Example for ~30 fps

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from camera stream.")
                break # Exit the loop on disconnect
            except Exception as e:
                logger.error(f"Error during WebSocket camera stream: {e}")
                # Depending on error severity, might need to break or close connection
                await websocket.close(code=status.WS_500_INTERNAL_ERROR, reason=f"Server error: {e}")
                break # Exit the loop on other errors

    finally:
        # The camera dependency handles its own cleanup via the yield/finally block
        logger.info("Exiting WebSocket camera stream.") 