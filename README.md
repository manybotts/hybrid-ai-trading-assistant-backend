[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?template=https://github.com/manybotts/hybrid-ai-trading-assistant-backend&envs=DERIVED_API_KEY,DERIVED_APP_ID,CALLS_PER_MINUTE,CALLS_PER_SECOND&DERIVED_API_KEY_DESCRIPTION=Your+Deriv.com+API+token&DERIVED_APP_ID_DESCRIPTION=Your+Deriv.com+App+ID&CALLS_PER_MINUTE_DESCRIPTION=Optional:+Override+default+calls+per+minute&CALLS_PER_SECOND_DESCRIPTION=Optional:+Override+default+calls+per+second&referral=main)
This repository contains the backend (API server) for the Hybrid AI Trading Assistant project. It uses FastAPI and TensorFlow to provide predictions of the next digit in a financial time series from Deriv.com.

## Project Overview

This backend provides a REST API that serves a trained TensorFlow model. The model predicts the probability distribution of the next digit in a sequence from the Deriv.com trading platform. The backend handles:

*   Connecting to the Deriv.com API via WebSockets.
*   Subscribing to a real-time tick stream.
*   Fetching historical data for training.
*   Making predictions using the trained model.
*   Providing API endpoints for:
    *   Getting predictions based on a user-provided sequence.
    *   Getting predictions based on the live data stream.
    *   Reloading the trained model.
    *   Setting the trading symbol.
* Dynamic Rate Limiting

## Prerequisites

*   **Python 3.7+:**  Ensure you have Python 3.7 or higher installed.
*   **pip:**  The Python package installer.
*   **Deriv.com Account:** You need an account on Deriv.com.
*   **Deriv.com API Token and App ID:** You need to generate an API token and obtain your App ID from your Deriv.com account settings.  This is *critical* for the application to function.
*   **Trained TensorFlow Model:**  You need a trained TensorFlow model saved as `digit_prediction_model.h5`.  See the "Training the Model" section below for instructions.
* **Railway Account:** You will need a Railway account.

## Installation and Local Execution (Optional - For Development)

These steps are for running the backend *locally* for development and testing.  For production deployment, see the "Deployment to Railway" section below.

1.  **Clone the repository:**

    ```bash
    git clone <your_backend_repo_url>
    cd hybrid-ai-trading-assistant-backend
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file (LOCAL DEVELOPMENT ONLY):**

    Create a file named `.env` in the `hybrid-ai-trading-assistant-backend` directory.  Add the following lines, replacing the placeholders with your actual values:

    ```
    DERIVED_API_KEY=your_deriv_api_key
    DERIVED_APP_ID=your_deriv_app_id
    ```
    **Do *not* commit this `.env` file to your repository!**

4.  **Run the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    The `--reload` flag automatically restarts the server when you make code changes.

5.  **Access the API:** The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API Endpoints

*   **`/` (GET):** A simple endpoint that returns a welcome message.
*   **`/predict` (POST):** Predicts the probability distribution for the next digit, given a sequence of digits.
    *   Request body: `{"digits": [1, 2, 3, ..., 9, 0]}` (a list of 50 integers)
    *   Response body: `{"probabilities": [0.1, 0.05, ..., 0.2], "predicted_digit": 7}`
*   **`/predict_live` (GET):** Predicts the probability distribution for the next digit using the live data stream.
    *   Response body: `{"probabilities": [0.1, 0.05, ..., 0.2], "predicted_digit": 7}` or `{"probabilities": [], "predicted_digit": -1}` if not enough data is available.
*   **`/reload_model` (POST):** Reloads the trained model from disk. Useful if you've retrained the model.
*   **`/set_symbol` (POST):** Sets the trading symbol (e.g., "R_100").
    *   Request body: `{"symbol": "R_100"}`

## Training the Model
To train the model, you can run the `ai_model.py` script. First you will need to obtain historical data. You can obtain this data from your Deriv account, or by utilizing the `derived_api.py` to call `get_historical_digits`. You can run the python script as is and modify the hyperparameters at the top of the file. Be sure to
## Deployment to Railway

This section describes how to deploy the backend to Railway. We'll use Railway's one-click deploy feature and a `railway.json` file for a streamlined deployment.

1.  **Create a Railway Account:** If you don't already have one, sign up for a free Railway account at [https://railway.app](https://railway.app).

2.  **One-Click Deploy:** Click the button below to deploy the backend to Railway:

    [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?template=https%3A%2F%2Fgithub.com%2Fmanybotts%2Fhybrid-ai-trading-assistant-backend&envs=DERIVED_API_KEY%2CDERIVED_APP_ID&optionalEnvs=CALLS_PER_MINUTE%2CCALLS_PER_SECOND&DERIVED_API_KEY_DESCRIPTION=Your+Deriv.com+API+token&DERIVED_APP_ID_DESCRIPTION=Your+Deriv.com+App+ID&CALLS_PER_MINUTE_DESCRIPTION=Optional%3A+Override+default+calls+per+minute&CALLS_PER_SECOND_DESCRIPTION=Optional%3A+Override+default+calls+per+second)

    *   This button will take you to Railway and guide you through the deployment process.  It will automatically:
        *   Fork the `hybrid-ai-trading-assistant-backend` repository into your Railway account.
        *   Prompt you to enter the required environment variables (see below).
        *   Build and deploy the application.

3.  **Environment Variables (REQUIRED):**

    During the one-click deployment (or manually if you prefer), you *must* set the following environment variables in your Railway project settings:

    *   `DERIVED_API_KEY`: Your Deriv.com API token (e.g., `abcdefg1234567`).  **This is critical for security. Do *not* skip this step.**
    *   `DERIVED_APP_ID`: Your Deriv.com App ID (e.g., `12345`).  **This is critical. Do *not* skip this step.**
    *   `CALLS_PER_MINUTE` (Optional): Override the dynamically fetched calls per minute.
    *   `CALLS_PER_SECOND` (Optional): Override the dynamically fetched calls per second.
    *    `PORT` (Optional): You can often leave it as Railway's default.

4. **Build and Start Command**
    * Go to "Settings".
    * Under "Build", you might not need a build command since requirements.txt is present, Railway should automatically use pip. If it *doesn't* automatically detect it, set the **Build Command** to: `pip install -r requirements.txt`
    * Under "Deploy", set the **Start Command** to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  **Get Your App's URL:** Once deployed, Railway will provide you with a public URL for your backend service. You'll need this URL for your frontend application.  Find this in the "Settings" tab under "Domains".

---
