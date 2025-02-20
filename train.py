# hybrid-ai-trading-assistant-backend/train.py
import asyncio
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from sklearn.model_selection import train_test_split
import derived_api  # Reuse the existing derived_api.py
import os


# --- Configuration ---
SEQUENCE_LENGTH = 50
NUM_DIGITS = 10
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1
NUM_HISTORICAL_DIGITS = 10000  # Adjust as needed
BATCH_SIZE = 64
EPOCHS = 10  # Adjust as needed
LSTM_UNITS = 128
LEARNING_RATE = 0.001
MODEL_FILE = "digit_prediction_model.h5"

# --- Deriv API Symbol ---
SYMBOL = os.getenv("SYMBOL", "R_100")  # Get from environment variable, default to R_100

# --- Data Preprocessing ---

async def load_and_preprocess_data(use_api=True, filepath="historical_digits.csv"):
    """Loads digit data, preprocesses, and splits into train/val/test."""
    if use_api:
        digits = await derived_api.get_historical_digits(symbol=SYMBOL, count=NUM_HISTORICAL_DIGITS)
        if not digits:
            print("Failed to fetch from API. Trying CSV...")
            use_api = False

    if not use_api:
        try:
            df = pd.read_csv(filepath)
            if 'digit' not in df.columns:
                raise ValueError("CSV must have 'digit' column.")
            digits = df['digit'].values
        except FileNotFoundError:
            print(f"ERROR: File not found: {filepath}")
            return None, None, None, None

    if not digits:
        return None, None, None, None

    sequences, next_digits = create_sequences(digits, SEQUENCE_LENGTH)
    X = np.array(sequences)
    y = np.array(next_digits)
    y = tf.keras.utils.to_categorical(y, num_classes=NUM_DIGITS)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=TEST_SIZE + VALIDATION_SIZE, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=TEST_SIZE / (TEST_SIZE + VALIDATION_SIZE),
                                                    random_state=42)
    return X_train, X_val, X_test, y_train, y_val, y_test

def create_sequences(digits, sequence_length):
    """Creates sequences of input digits and corresponding next digits."""
    sequences = []
    next_digits = []
    for i in range(len(digits) - sequence_length):
        sequences.append(digits[i:i + sequence_length])
        next_digits.append(digits[i + sequence_length])
    return sequences, next_digits

# --- Model Definition ---

def create_lstm_model(sequence_length=SEQUENCE_LENGTH, num_digits=NUM_DIGITS, lstm_units=LSTM_UNITS, learning_rate=LEARNING_RATE):
    """Creates and compiles the LSTM model."""
    model = Sequential()
    model.add(Embedding(input_dim=num_digits, output_dim=50, input_length=sequence_length))
    model.add(LSTM(lstm_units, return_sequences=True))
    model.add(LSTM(int(lstm_units / 2)))
    model.add(Dense(num_digits, activation='softmax'))
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model

async def train_model():
    """Fetches data, trains the model, and saves it locally."""
    print("Starting model training...")

    # Fetch Rate Limits (important for API usage)
    await derived_api.get_rate_limits()

    X_train, X_val, X_test, y_train, y_val, y_test = await load_and_preprocess_data(use_api=True)

    if X_train is None:
        print("Error: Could not load data. Exiting.")
        return

    model = create_lstm_model()
    model.summary()

    print("Training the model...")
    history = model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=(X_val, y_val))

    print("Evaluating the model...")
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss:.4f}")
    print(f"Test Accuracy: {accuracy:.4f}")

    # Save model locally
    model.save(MODEL_FILE)
    print(f"Model saved locally to {MODEL_FILE}")

if __name__ == "__main__":
    asyncio.run(train_model())
