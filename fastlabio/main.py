# Path: main.py
# -*- coding: utf-8 -*-
"""
Main entry point for the Fast Lab IO FastAPI application.

This module initializes the FastAPI application, sets up basic logging,
and includes a root endpoint for initial verification. It serves as the
foundation for integrating instrument control libraries like pysilico and
plico_motor.
"""

__author__ = "Marco Bonaglia" # Placeholder
__version__ = "0.1.0"
__date__ = "2025-05-27" # Placeholder - use current date

import logging
from fastapi import FastAPI

# Import the camera router
# from .camera import camera_router # Remove relative import
from fastlabio.camera import camera_router # Use absolute import relative to package root

# Import the motor router
from fastlabio.motor import motor_router # Use absolute import relative to package root

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Fast Lab IO API",
              description="API for controlling laboratory instruments via FastAPI.",
              version=__version__)

@app.get("/")
async def read_root():
    """
    Root endpoint providing a welcome message.
    """
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to the Fast Lab IO API"}

# Future Routers/Includes will be added here
# app.include_router(camera_router, prefix="/camera", tags=["camera"])
# app.include_router(motor_router, prefix="/motor", tags=["motor"])

# Include the camera router
app.include_router(camera_router, prefix="/camera", tags=["camera"])

# Include the motor router
app.include_router(motor_router, prefix="/motor", tags=["motor"]) 