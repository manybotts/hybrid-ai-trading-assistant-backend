# Hybrid AI Trading Assistant - Backend

This repository contains the backend (API server) for the Hybrid AI Trading Assistant project.  It uses FastAPI and TensorFlow to provide predictions of the next digit in a financial time series from Deriv.com.

## Prerequisites

*   Python 3.7+
*   pip
*   A Deriv.com account and API token.
*   A trained TensorFlow model (`digit_prediction_model.h5`). See the Training section below.

## Installation

1.  Clone the repository:
    ```bash
    git clone <your_backend_repo_url>
    cd hybrid-ai-trading-assistant-backend
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (IMPORTANT!)

**You *must* configure the following environment variables before running the application.**  Do this *directly on the Railway platform* after deploying.  Do *not* use a `.env` file in production.

*   `DERIVED_API_KEY`: Your Deriv.com API token.
*   `DERIVED_APP_ID`: Your Deriv.com App ID.
*   `CALLS_PER_MINUTE` (Optional): Override the dynamically fetched calls per minute.
*    `CALLS_PER_SECOND` (Optional): Override the dynamically fetched calls per second.

## Running Locally (For Development/Testing ONLY)
Although you are skipping the local .env you can still run locally for quick testing.
1.  **Temporarily** set the environment variables in your shell:
    ```bash
    export DERIVED_API_KEY=your_api_key
    export DERIVED_APP_ID=your_app_id
    # Optionally, set CALLS_PER_MINUTE and CALLS_PER_SECOND
    ```
2.  Run the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
    The `--reload` flag automatically restarts the server when you make code changes.

3.  The API will be available at `http://127.0.0.1:8000`.  You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

*   **`/` (GET):**  A simple endpoint that returns a welcome message.
*   **`/predict` (POST):**  Predicts the probability distribution for the next digit, given a sequence of digits.
    *   Request body: `{"digits": [1, 2, 3, ..., 9, 0]}` (a list of 50 integers)
    *   Response body: `{"probabilities": [0.1, 0.05, ..., 0.2], "predicted_digit": 7}`
*   **`/predict_live` (GET):**  Predicts the probability distribution for the next digit using the live data stream.
    *   Response body:  `{"probabilities": [0.1, 0.05, ..., 0.2], "predicted_digit": 7}`  or `{"probabilities": [], "predicted_digit": -1}` if not enough data is available.
*   **`/reload_model` (POST):** Reloads the trained model from disk. Useful if you've retrained the model.
*   **`/set_symbol` (POST):**  Sets the trading symbol (e.g., "R_100").
    * Request body: `{"symbol" : "R_100"}`

## Deployment to Railway

1.  **Create a new Railway project.**
2.  **Connect your GitHub repository (`hybrid-ai-trading-assistant-backend`).**
3.  **Add Environment Variables:**
    *   Go to the "Variables" tab in your Railway project settings.
    *   Add the following variables:
        *   `DERIVED_API_KEY` (your API key)
        *   `DERIVED_APP_ID` (your App ID)
        * Add `CALLS_PER_MINUTE` and `CALLS_PER_SECOND` if you need to override defaults.
4.  **Deployment Settings**
    * Go to settings, and set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.
