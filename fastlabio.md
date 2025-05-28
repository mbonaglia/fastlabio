# Fast Lab IO: AI-Optimized Project Breakdown

## 1. Overview

This document outlines the sequential phases and activities for building a FastAPI-based instrument control system integrating `pysilico` (camera) and `plico_motor` (motor) libraries. Each phase is broken down into activities with clear goals, steps, and verification criteria.

---

## 2. Phases and Activities

### Phase 1: Initial Setup and Pysilico Camera Integration

#### Activity 1.1: Project Initialization
- **Goal:** Create the basic FastAPI project structure.
- **Steps:**
  - Initialize a Python virtual environment.
  - Install core libraries: `fastapi`, `uvicorn[standard]`, `pydantic`.
  - Set up a `main.py` file with FastAPI app initialization and logging.
- **Verification:**
  - Run `uvicorn main:app --reload`.
  - Ensure Swagger UI is accessible.

#### Activity 1.2: Pysilico Library Integration and Dependency
- **Goal:** Integrate the `pysilico` client library and create a robust dependency for camera instances.
- **Steps:**
  - Install `pysilico` and `opencv-python`.
  - Implement `async def get_pysilico_camera()`:
    - Use `await asyncio.to_thread()` for `pysilico.camera()`.
    - Add try/except/finally for error handling and resource cleanup.
    - Define `CAMERA_HOST` and `CAMERA_PORT` constants.
- **Verification:**
  - Simulate `pysilico-server` unavailability.
  - Ensure `get_pysilico_camera` handles `HTTPException` correctly.

#### Activity 1.3: Single Frame Acquisition Endpoint
- **Goal:** Create an API endpoint to acquire a single image frame from the camera.
- **Steps:**
  - Implement `@router.get("/camera/frame")` endpoint.
  - Use `Depends(get_pysilico_camera)`.
  - Call `camera.getFutureFrames(1)` within `await asyncio.to_thread()`.
  - Encode image to JPEG using `cv2.imencode()`.
  - Return `StreamingResponse` with `media_type="image/jpeg"`.
  - Add error handling for no frames received or encoding failures.
- **Verification:**
  - Test via Swagger UI or HTML client.
  - Verify image display.

#### Activity 1.4: Camera Parameter Control Endpoints
- **Goal:** Implement endpoints for adjusting camera parameters.
- **Steps:**
  - Define Pydantic models: `ExposureSettings`, `GainSettings` (with validation, e.g., `gt=0`).
  - Create endpoints:
    - `PUT /camera/exposure` → `set_exposure()`
    - `PUT /camera/gain` → `set_gain()`
  - Use `Depends(get_pysilico_camera)`.
  - Wrap camera methods with `await asyncio.to_thread()`.
  - Return success messages; handle errors.
- **Verification:**
  - Test via Swagger UI or HTML client with valid/invalid values.

#### Activity 1.5: Real-time Camera Stream WebSocket Endpoint
- **Goal:** Develop a WebSocket endpoint for continuous, real-time video streaming from the camera.
- **Steps:**
  - Implement `@router.websocket("/ws/camera/stream")`.
  - Accept connection with `await websocket.accept()`.
  - Loop to acquire frames using `camera.getFutureFrames(1)` via `await asyncio.to_thread()`.
  - Encode frame to JPEG and send via `await websocket.send_bytes()`.
  - Handle `WebSocketDisconnect` and log exceptions.
- **Verification:**
  - Use HTML client to start/stop stream.
  - Verify continuous video feed and client disconnection handling.

#### Activity 1.6: Basic HTML Frontend for Testing
- **Goal:** Provide a simple HTML page to interact with the API.
- **Steps:**
  - Implement `@app.get("/", response_class=HTMLResponse)` endpoint.
  - Embed provided HTML/JS for client-side interaction.
  - Ensure JS functions interact with FastAPI endpoints.
- **Verification:**
  - Open root URL in browser.
  - Verify all buttons and stream functionality.

---

### Phase 2: Plico_Motor Integration

#### Activity 2.1: Plico_Motor Client Integration and Dependency
- **Goal:** Integrate the `plico_motor` client library and create a dependency for motor instances.
- **Steps:**
  - Research `plico_motor` client usage (e.g., `plico.motor.motor_client('IP', PORT)`).
  - Implement `async def get_plico_motor()` as an async dependency, mirroring `get_pysilico_camera()`.
  - Use `await asyncio.to_thread()` for blocking calls.
  - Add robust error handling and resource release.
- **Verification:**
  - Write a test script to ensure `get_plico_motor()` connects and handles errors correctly.

#### Activity 2.2: Motor Control Endpoints
- **Goal:** Create API endpoints for controlling motor position and speed.
- **Steps:**
  - Define Pydantic models for motor commands (e.g., `MotorMoveRequest(position: float)`, `MotorSpeedRequest(speed: float)`).
  - Create endpoints:
    - `PUT /motor/move` → `move_motor()`
    - `GET /motor/position` → `get_motor_position()`
    - `PUT /motor/speed` → `set_motor_speed()`
  - Wrap `plico_motor` methods with `await asyncio.to_thread()`.
  - Add comprehensive error handling.
- **Verification:**
  - Test via Swagger UI: move motor, set speed, verify position readings.

#### Activity 2.3: Real-time Motor Status WebSocket (Optional)
- **Goal:** Implement a WebSocket for streaming real-time motor status.
- **Steps:**
  - Research if `plico_motor` supports real-time status callbacks or efficient polling.
  - If supported, implement `@router.websocket("/ws/motor/stream")`.
  - Continuously fetch or receive motor status and send as JSON over WebSocket.
- **Verification:**
  - Create HTML/JS client to visualize real-time motor status.

---

### Phase 3: Advanced Features and Deployment

#### Activity 3.1: Shared Instrument State Management
- **Goal:** Manage shared state (e.g., active camera/motor connections) across API endpoints.
- **Steps:**
  - Define a class/module to manage active `pysilico` and `plico_motor` instances.
  - Update dependencies to use shared state (singleton/pooling pattern).
- **Verification:**
  - Ensure multiple API calls reuse the same instrument instances.

#### Activity 3.2: Long-Running Task Management (Conceptual)
- **Goal:** Outline strategies for handling long-running scientific operations.
- **Steps:**
  - Document client timeout issues for long tasks.
  - Propose integration with async task queues (e.g., Celery, RQ).
  - Explain pattern: endpoint triggers background task, returns task ID; WebSocket for status/progress.
- **Verification:**
  - (Conceptual only; no code required.)

#### Activity 3.3: Production Deployment with Docker
- **Goal:** Prepare FastAPI app for production deployment using Docker.
- **Steps:**
  - Create a Dockerfile for the application.
  - Ensure all dependencies are installed in the Docker image.
  - Document requirement for `pysilico-server`, Vimba driver, and `plico_motor` server/drivers to run on the instrument machine (not in Docker).
  - Explain Docker's role in consistent, reproducible environments.
  - Suggest Gunicorn for process management in production.
- **Verification:**
  - Build Docker image.
  - Run container and verify FastAPI accessibility.
  - (Full instrument testing requires external servers.)

---

## 3. Workflow

- **Iterative, test-driven development:**
  - Build complexity incrementally, phase by phase.
  - Use checkpoints after each phase to ensure functionality.

### Phase 1: Pysilico Camera Control Core
- Complete Activities 1.1–1.6.
- **Checkpoint:** All camera endpoints and WebSocket stream functional.

### Phase 2: Plico_Motor Integration
- Complete Activities 2.1–2.3.
- **Checkpoint:** All motor endpoints functional.

### Phase 3: Refinement and Deployment
- Complete Activities 3.1–3.3.
- **Checkpoint:** Application is modular, documented, and deployment-ready.

---

## 4. Coding Practices

- Use clear variable names.
- Add comments where necessary.
- Commit changes frequently.
- Use FastAPI's Swagger UI for API testing.