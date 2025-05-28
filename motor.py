# Path: fastlabio/motor.py
# -*- coding: utf-8 -*-
"""
Motor module for Fast Lab IO.

This module provides the FastAPI router and dependency functions for interacting
with the plico_motor motor stages.
"""

__author__ = "Marco Bonaglia" # Placeholder
__version__ = "0.1.0"
__date__ = "2025-05-27" # Placeholder - use current date

import asyncio
import logging
from fastapi import HTTPException, status, APIRouter, Depends
from pydantic import BaseModel, Field # Import BaseModel and Field

# Assuming plico.motor provides the motor client
# from plico.motor.motor_client import MotorClient # Example import - adjust based on actual library structure
# import plico.motor
# from plico.motor import motor_client # Import motor_client directly
import plico_motor # Import the plico_motor package directly
from plico_motor.client.motor_client import MotorClient # Import MotorClient for type hinting

# Set up logging for this module
logger = logging.getLogger(__name__)

# Configuration constants (placeholders)
MOTOR_HOST = "localhost" # Replace with actual motor server IP
MOTOR_PORT = 7200        # Replace with actual motor server port

motor_router = APIRouter()

# Pydantic models for motor requests
class MotorMoveRequest(BaseModel):
    """Pydantic model for motor move command."""
    position: float = Field(..., description="Target position for the motor")

class MotorSpeedRequest(BaseModel):
    """
Pydantic model for motor speed setting.

Note: Validate speed range based on specific motor capabilities if known.
"""
    speed: float = Field(..., ge=0, description="Motor speed value") # Adjust ge/le based on motor spec

async def get_plico_motor():
    """
    FastAPI dependency to get a plico_motor motor instance.

    Connects to the plico_motor server and yields the motor instance.
    Ensures the connection is closed afterwards.
    Handles connection errors by raising HTTPException.
    """
    # Initialize motor_instance to None before the try block
    motor_instance = None
    try:
        # Connect to the motor server, wrapping the blocking call if necessary
        # The exact client connection method might vary, check plico.motor docs
        logger.info(f"Attempting to connect to motor at {MOTOR_HOST}:{MOTOR_PORT}")

        # Use asyncio.wait_for with asyncio.to_thread to add a timeout to the blocking client connection
        timeout_seconds = 10 # Set a timeout value (e.g., 10 seconds)
        try:
            # Call the imported motor function using its module path and assign to motor_instance
            motor_instance = await asyncio.wait_for(
                asyncio.to_thread(plico_motor.motor, MOTOR_HOST, MOTOR_PORT, axis=1), # Use plico_motor.motor
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout while attempting to connect to motor at {MOTOR_HOST}:{MOTOR_PORT}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Timeout connecting to motor server on {MOTOR_HOST}:{MOTOR_PORT}. Server might be unresponsive."
            )

        # The following check is still relevant if the actual motor() function can return None
        if motor_instance is None:
            logger.error("plico_motor.motor() returned None. Check plico_motor_server logs for details.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to obtain motor client from server. Check server logs."
            )

        logger.info("Motor connection successful (using real client)." if hasattr(motor_instance, 'close') else "Motor connection successful (client may not have close method).")
        yield motor_instance
    except Exception as e:
        logger.error(f"Error connecting to motor: {e}")
        # Re-raise the exception as HTTPException for FastAPI to handle
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not connect to motor: {e}"
        )
    finally:
        if motor_instance and hasattr(motor_instance, 'close'):
            # Assuming plico_motor client object has a close or similar method
            # await asyncio.to_thread(motor_instance.close) # Uncomment and adjust if actual close method is blocking
            pass # Using pass for the mock client

# Future motor endpoints will be added here using motor_router

# @motor_router.put("/move")
# async def move_motor(request: MotorMoveRequest, motor: plico.motor.MotorClient = Depends(get_plico_motor)):
#     # ... endpoint logic ... 

@motor_router.put("/move")
async def move_motor(request: MotorMoveRequest, motor: MotorClient = Depends(get_plico_motor)):
    """
    Move the motor to a specified position.

    Args:
        request: Motor move request including the target position.
        motor: The plico_motor motor instance provided by the dependency.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If there is an error moving the motor.
    """
    try:
        logger.info(f"Received request to move motor to position: {request.position}")
        # Call the motor's move method, wrapping with asyncio.to_thread if blocking
        await asyncio.to_thread(motor.move, request.position) # Use the mock move method for now
        logger.info("Motor move command sent successfully.")
        return {"message": f"Motor moving to position: {request.position}"}
    except Exception as e:
        logger.error(f"Error moving motor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not move motor: {e}"
        )

@motor_router.get("/position")
async def get_motor_position(motor: MotorClient = Depends(get_plico_motor)):
    """
    Get the current position of the motor.

    Args:
        motor: The plico_motor motor instance provided by the dependency.

    Returns:
        A dictionary containing the current motor position.

    Raises:
        HTTPException: If there is an error getting the motor position.
    """
    try:
        logger.info("Received request to get motor position.")
        # Call the motor's get_position method, wrapping with asyncio.to_thread if blocking
        position = await asyncio.to_thread(motor.get_position) # Use the mock get_position method for now
        logger.info(f"Retrieved motor position: {position}")
        return {"position": position}
    except Exception as e:
        logger.error(f"Error getting motor position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not get motor position: {e}"
        )

@motor_router.put("/speed")
async def set_motor_speed(request: MotorSpeedRequest, motor: MotorClient = Depends(get_plico_motor)):
    """
    Set the speed of the motor.

    Args:
        request: Motor speed request including the desired speed.
        motor: The plico_motor motor instance provided by the dependency.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If there is an error setting the motor speed.
    """
    try:
        logger.info(f"Received request to set motor speed to: {request.speed}")
        # Call the motor's set_speed method, wrapping with asyncio.to_thread if blocking
        await asyncio.to_thread(motor.set_speed, request.speed) # Use the mock set_speed method for now
        logger.info("Motor speed set command sent successfully.")
        return {"message": f"Motor speed set to: {request.speed}"}
    except Exception as e:
        logger.error(f"Error setting motor speed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not set motor speed: {e}"
        ) 