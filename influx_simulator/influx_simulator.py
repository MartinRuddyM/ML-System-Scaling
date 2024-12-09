import pandas as pd
import os
import time
import json
import random
import paho.mqtt.client as mqtt

# MQTT Broker Configuration
BROKER_ADDRESS = "rabbitmq"
BROKER_PORT = 1883

# Paths to datasets
HOUSING_DATA_PATH = "data/HousingData.csv"
WINE_DATA_PATH = "data/WineQT.csv"
IMAGE_FOLDER_PATH = "data/images"

# Features and target variables for each model
HOUSING_FEATURES = ['RM', 'LSTAT', 'PTRATIO', 'INDUS', 'NOX']
HOUSING_TARGET = 'MEDV'

WINE_FEATURES = ['fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar', 'chlorides', 
                 'free sulfur dioxide', 'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol']
WINE_TARGET = 'quality'

# Load datasets
housing_data = pd.read_csv(HOUSING_DATA_PATH)
wine_data = pd.read_csv(WINE_DATA_PATH)

# MQTT Publisher Initialization
client = mqtt.Client()
client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

def publish_data(topic, payload):
    """Publish data to the MQTT broker."""
    client.publish(topic, json.dumps(payload))

def send_data(more_image=False):
    """Generate and send data for each model."""
    housing_sample = housing_data.sample(1).iloc[0]
    wine_sample = wine_data.sample(1).iloc[0]

    for _ in range(2):
        # Housing Data (Linear Regression)
        housing_payload = {
            "type": "numeric",
            "features": housing_sample[HOUSING_FEATURES].tolist(),
            "target": housing_sample[HOUSING_TARGET]
        }
        publish_data("data_influx", housing_payload)

    for _ in range(2):
        # Wine Data (XGBoost)
        wine_payload = {
            "type": "classification",
            "features": wine_sample[WINE_FEATURES].tolist(),
            "target": wine_sample[WINE_TARGET]
        }
        publish_data("data_influx", wine_payload)

    for _ in range(2 if more_image else 1):
        image_file = random.choice(os.listdir(IMAGE_FOLDER_PATH))
        image_path = f"images/{image_file}"

        # Image Data (ResNet-50)
        image_payload = {
            "type": "image",
            "image_path": image_path
        }
        publish_data("data_influx", image_payload)

def simulate_flow():
    """Simulate changing data flow and distribution."""
    current_mode = "balanced"
    start_time = time.time()

    while time.time() - start_time < 420:  # Run for 7 minutes
        #send_data()

        # Change flow every minute
        elapsed = time.time() - start_time
        if elapsed < 60:  # Minute 1: Balanced data
            current_mode = "balanced"
        elif elapsed < 120:  # Minute 2: Increase all data
            #current_mode = "all_increased"
            current_mode = "image_focus"
        elif elapsed < 180:  # Minute 3: Back to balanced
            current_mode = "image_focus"
        elif elapsed < 240:  # Minute 4: Focus on image data
            current_mode = "balanced"
        elif elapsed < 300:  # Minute 5: Back to balanced
            current_mode = "balanced"
        else: # Minutes 6 & 7 all increased
            current_mode = "all_increased"

        # Publish based on current mode
        if current_mode == "balanced":
            send_data()
        elif current_mode == "all_increased":
            send_data()
            send_data()  # Send data twice as fast
        elif current_mode == "image_focus":
            send_data(more_image=True)

        time.sleep(2)

if __name__ == "__main__":
    print("Starting Data Influx Simulator...")
    simulate_flow()
