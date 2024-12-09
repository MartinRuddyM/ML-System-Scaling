from flask import Flask
import requests
import paho.mqtt.client as mqtt
import json
from prometheus_client import Counter, start_http_server, CollectorRegistry, Gauge, push_to_gateway
import psutil
import threading
import docker
import time
import subprocess
from threading import Lock

# Initialize Flask app
app = Flask(__name__)

# MQTT Configuration
BROKER_ADDRESS = "rabbitmq"
BROKER_PORT = 1883
MQTT_TOPIC = "data_influx"

#scaled_horizontally = False
#skipped_previous_horizontally = False

# Model endpoints
MODEL_ENDPOINTS = {
    "numeric": "http://linear_model:5001/predict",
    "classification": "http://xgboost_model:5002/predict",
    "image": "http://image_model:5003/predict",
}

# Prometheus Metrics
requests_counter = Counter('requests_total', 'Total requests to the app')
errors_counter = Counter('errors_total', 'Total errors in the app')
network_sent_gauge = Gauge('network_sent_bytes', 'Total network sent in bytes')
network_received_gauge = Gauge('network_received_bytes', 'Total network received in bytes')

# Global variables to simulate horizontal scaling
image_model_replicas = 1  # Start with 1 container
scaling_in_progress = False
scaling_lock = Lock()  # To handle concurrency safely

# MQTT Client
mqtt_client = mqtt.Client()

def process_message(data):
    """Route data to the appropriate model."""
    global image_model_replicas  # Track the current number of replicas
    try:
        data_type = data.get("type")

        if data_type not in MODEL_ENDPOINTS:
            errors_counter.inc()
            return {"error": f"Unsupported data type: {data_type}"}

        # Send features or image path to the model container
        if data_type != 'image':
            features = data.get("features")
            payload = {"features": features}
        else:
            image_path = data.get("image_path")
            payload = {"image_path": image_path}

        response = requests.post(MODEL_ENDPOINTS[data_type], json=payload)

        if response.status_code == 200:
            requests_counter.inc()
            return response.json()
        else:
            errors_counter.inc()
            return {"error": f"Error from model: {response.text}"}

    except Exception as e:
        errors_counter.inc()
        return {"error": str(e)}

    except Exception as e:
        errors_counter.inc()
        return {"error": str(e)}

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    try:
        data = json.loads(msg.payload.decode())
        data_type = data.get("type")
        # Simulate reduced flow for image data based on replicas for horizontal scaling
        if data_type == 'image' and hash(data.get("image_path")) % image_model_replicas != 0:
            print("Skipped image data due to horizontal scaling simulation", flush=True)
            return
        result = process_message(data)
        #print(f"Processed result: {result}")
    except Exception as e:
        errors_counter.inc()
        print(f"Error processing message: {str(e)}")


def monitor_system():
    """Monitor system metrics and Docker container metrics continuously."""
    while True:
        try:
            # Update system metrics
            net_io = psutil.net_io_counters()
            network_sent_gauge.set(net_io.bytes_sent)
            network_received_gauge.set(net_io.bytes_recv)

        except Exception as e:
            print(f"Error monitoring system or containers: {e}")
        
        time.sleep(1)

def scale_vertical(container_name, cpu_limit):
    """Adjust CPU allocation for a container."""
    try:
        subprocess.run(["docker", "update", "--cpus", str(cpu_limit), container_name], check=True)
        print(f"Scaled vertically: {container_name} updated to {cpu_limit} CPUs.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"Error scaling vertically: {e}")

def scale_horizontal(service_name, replicas):
    """Scale a service horizontally to the specified number of replicas."""
    global scaling_in_progress, image_model_replicas

    with scaling_lock:
        if scaling_in_progress:
            print("Scaling operation already in progress. Skipping.")
            return {"info": "Scaling in progress, try again later."}

        scaling_in_progress = True  # Lock scaling process
        print(f"Scaling {service_name} to {replicas} replicas...", flush=True)

    try:
        time.sleep(15)  # Simulated delay for setting up replicas
        image_model_replicas = replicas
        print(f"Scaling complete. Current replicas: {image_model_replicas}", flush=True)
    except Exception as e:
        print(f"Error during scaling: {str(e)}")
    finally:
        with scaling_lock:
            scaling_in_progress = False  # Unlock scaling process

def monitor_and_scale(strategy="horizontal", cpu_threshold_up=80, cpu_threshold_down=35):
    """Fetch and push container stats to Prometheus and apply scaling to the image model."""
    client = docker.from_env()

    # Name mapping for Prometheus labels
    name_mapping = {
        'image': 'Image model'}
    """,
        'linear': 'Linear model',
        'xgboost': 'XGBoost model',
        'app-1': 'App'
    }"""

    # Setup Prometheus registry and Gauges
    registry = CollectorRegistry()
    container_cpu_usage = Gauge('container_cpu_usage', 'CPU usage of Docker container', ['container_name'], registry=registry)
    container_memory_usage = Gauge('container_memory_usage', 'Memory usage of Docker container', ['container_name'], registry=registry)

    # Identify relevant containers
    relevant_containers = []
    image_model_container = None
    for container in client.containers.list():
        if any(keyword in container.name.lower() for keyword in name_mapping):
            relevant_containers.append(container)
        if "image_model" in container.name.lower():
            image_model_container = container

    if not image_model_container:
        print("Image model container not found!")
        return

    # Scaling variables
    current_replicas = 1
    current_cpus = 1.0
    scaled = False
    CPU_readings = []
    counter = 0

    while True:
        try:
            for container in relevant_containers: # Always read the CPU usage (every second)
                readable_name = next(value for key, value in name_mapping.items() if key in container.name.lower())

                # Fetch container stats (not streaming)
                stats = container.stats(stream=False)

                # Extract CPU and memory usage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                cpu_usage = (cpu_delta / system_cpu_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100 / current_cpus
                mem_usage = stats['memory_stats']['usage'] / stats['memory_stats']['limit'] * 100
                CPU_readings.append(cpu_usage)
            if counter == 0: # Only every 5 seconds report the averaged data
                cpu_usage = sum(CPU_readings) / len(CPU_readings)
                CPU_readings = []

                # Push metrics to Prometheus
                container_cpu_usage.labels(container_name=readable_name).set(cpu_usage)
                container_memory_usage.labels(container_name=readable_name).set(mem_usage)
                # Push the metrics to the Pushgateway
                push_to_gateway('pushgateway:9091', job='docker_metrics', registry=registry)
                # Scaling logic only for the image model
                if container == image_model_container and not scaled:
                    print(f"Considering image CPU usage: {cpu_usage}",flush=True)
                    if cpu_usage >= cpu_threshold_up:
                        print(f"High CPU detected: {cpu_usage}%")
                        if strategy == "horizontal" and current_replicas < 3:
                            current_replicas += 1
                            scale_horizontal("image_model", current_replicas)
                            scaled = True
                        elif strategy == "vertical" and current_cpus < 3:
                            current_cpus += 1
                            scale_vertical(image_model_container.name, current_cpus)
                            scaled = True
                        else:
                            scaled = False
                    elif cpu_usage < cpu_threshold_down:
                        print(f"Low CPU detected: {cpu_usage}%")
                        if strategy == "horizontal" and current_replicas > 1:
                            current_replicas -= 1
                            scale_horizontal("image_model", current_replicas)
                            scaled = True
                        elif strategy == "vertical" and current_cpus > 1.0:
                            current_cpus -= 1
                            scale_vertical(image_model_container.name, current_cpus)
                            scaled = True
                        else:
                            scaled = False
                    else:
                        scaled = False
                else:
                    scaled = False

            # Sleep to avoid excessive monitoring
            time.sleep(1)
            counter = (counter + 1) % 5

        except Exception as e:
            print(f"Error during monitoring/scaling: {e}")
            time.sleep(5)



if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    # Update the metrics regularly
    threading.Thread(target=monitor_system, daemon=True).start()
    threading.Thread(target=monitor_and_scale, daemon=True).start()

    # Connect to MQTT Broker
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER_ADDRESS, BROKER_PORT)
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_start()

    # Run Flask app
    app.run(host="0.0.0.0", port=5000)
