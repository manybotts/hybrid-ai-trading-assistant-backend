# backend/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from . import derived_api  # Import from the same package
import asyncio
import os
from collections import deque

# --- Configuration (HARDCODED DEFAULTS - MUST BE REPLACED WITH ENV VARS) ---
MODEL_PATH = "digit_prediction_model.h5"  # Assume model is in the same directory
SEQUENCE_LENGTH = 50

# --- Load the Trained Model ---
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print(f"WARNING: Could not load model: {e}.  Ensure model exists.")
    model = None  # Allow startup to continue, but handle missing model

# --- FastAPI Setup ---
app = FastAPI()

# --- Data Structures (Pydantic Models) ---

class PredictionRequest(BaseModel):
    digits: list[int]

class PredictionResponse(BaseModel):
    probabilities: list[float]
    predicted_digit: int

# --- Global Variable for Latest Digits (using deque) ---
latest_digits_deque = deque(maxlen=SEQUENCE_LENGTH)

# --- Lock for Thread Safety ---
lock = asyncio.Lock()

async def get_lock():  # Dependency for FastAPI
    return lock

# --- Background Task for Streaming Data ---
async def get_streaming_digits(symbol: str = "R_100"):
    """Subscribes to Deriv tick stream and updates latest_digits_deque."""
    global latest_digits_deque
    reconnect_delay = 5

    while True:
        try:
            async for digit in derived_api.subscribe_to_ticks(symbol=symbol):
                async with lock:
                    latest_digits_deque.append(digit)
                reconnect_delay = 5  # Reset on success
        except Exception as e:
            print(f"Error in streaming digits: {e}, reconnecting in {reconnect_delay}s")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)


@app.on_event("startup")
async def startup_event():
    """Starts background tasks on app startup."""
    asyncio.create_task(get_streaming_digits())
    await derived_api.get_rate_limits()


# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Digit Prediction API"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, lock: asyncio.Lock = Depends(get_lock)):
    """Predicts next digit probabilities based on input sequence."""
    if model is None:  # Handle case where model failed to load
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        if len(request.digits) != SEQUENCE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Input must be {SEQUENCE_LENGTH} digits")
        if any(not 0 <= d <= 9 for d in request.digits):
            raise HTTPException(status_code=400, detail="Digits must be 0-9")

        async with lock:
            sequence = np.array(request.digits).reshape(1, SEQUENCE_LENGTH)
            prediction = model.predict(sequence, verbose=0)[0]
            predicted_digit = int(np.argmax(prediction))
        return PredictionResponse(probabilities=prediction.tolist(), predicted_digit=predicted_digit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict_live", response_model=PredictionResponse)
async def predict_live(lock: asyncio.Lock = Depends(get_lock)):
    """Predicts next digit probabilities using live data stream."""
    global latest_digits_deque
    if model is None:  # Handle case where model failed to load
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        async with lock:
            if len(latest_digits_deque) < SEQUENCE_LENGTH:
                return PredictionResponse(probabilities=[], predicted_digit=-1)

            sequence = np.array(latest_digits_deque).reshape(1, SEQUENCE_LENGTH)
            prediction = model.predict(sequence, verbose=0)[0]
            predicted_digit = int(np.argmax(prediction))
        return PredictionResponse(probabilities=prediction.tolist(), predicted_digit=predicted_digit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload_model")
async def reload_model(lock: asyncio.Lock = Depends(get_lock)):
    """Reloads the ML model from disk."""
    global model
    async with lock:
        try:
            model = tf.keras.models.load_model(MODEL_PATH)
            return {"message": "Model reloaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Placeholder endpoint for setting the symbol (to be integrated with the frontend)
@app.post("/set_symbol")
async def set_symbol(symbol: str, background_tasks: BackgroundTasks, lock: asyncio.Lock = Depends(get_lock)):
    """Sets the trading symbol and restarts the data streaming."""
    global latest_digits_deque
    async with lock:
      latest_digits_deque.clear()  # Clear the existing deque
    background_tasks.add_task(get_streaming_digits, symbol=symbol) #Restart background task
    return {"message": f"Symbol set to {symbol}"}
