# Hybrid AI Trading Assistant - Backend

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
**Part 2: `README.md` (Deployment to Railway)**

```markdown
## Deployment to Railway

This section describes how to deploy the backend to Railway.  We'll use Railway's one-click deploy feature for simplicity and to avoid storing secrets in the repository.

1.  **Create a Railway Account:** If you don't already have one, sign up for a free Railway account at [https://railway.app](https://railway.app).

2.  **Create a New Project:**  In your Railway dashboard, create a new project. Choose "Empty Project".

3.  **Create a New Service:** In your new project, add a new service, and select "GitHub Repo".

4.  **Connect to GitHub:**  Connect your Railway project to your `hybrid-ai-trading-assistant-backend` GitHub repository.  You'll need to grant Railway access to your repository.

5.  **Configure Environment Variables:**
    *   Go to the "Variables" tab in your Railway service settings.
    *   Add the following variables:
        *   `DERIVED_API_KEY`:  Your Deriv.com API token (e.g., `abcdefg1234567`).  **This is critical for security.  Do *not* skip this step.**
        *   `DERIVED_APP_ID`: Your Deriv.com App ID (e.g., `12345`).  **This is critical. Do *not* skip this step.**
        *   `CALLS_PER_MINUTE` (Optional): Override the dynamically fetched calls/minute.
        *   `CALLS_PER_SECOND` (Optional): Override the dynamically fetched calls/second.

6.  **Configure Build and Start Commands:**
      * Go to "Settings".
      * Under "Build", you might not need a build command since requirements.txt is present, Railway should automatically use pip.  If it *doesn't* automatically detect it, set the **Build Command** to: `pip install -r requirements.txt`
      * Under "Deploy", set the **Start Command** to: `uvicorn main:app --host 0.0.0.0 --port $PORT`

7.  **Deploy:** Railway should automatically deploy your application whenever you push changes to your `main` branch on GitHub.  You can also manually trigger a deployment from the Railway dashboard.

8. **Get your App's URL:** Once deployed, Railway will provide you with a public URL for your backend service.  You'll need this URL for your frontend application. You can find the url under the "Settings" tab, under "Domains".

## One-Click Deploy Button (Optional)
Include this button at the top of your readme:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/manybotts/hybrid-ai-trading-assistant-backend)
