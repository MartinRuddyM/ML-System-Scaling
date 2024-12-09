# Base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install required libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the simulator code and data into the container
COPY influx_simulator.py ./influx_simulator.py
COPY data ./data

# Expose any necessary ports (optional, MQTT typically uses 1883, but this is for the broker)
EXPOSE 1883

# Command to run the simulator
CMD ["python", "influx_simulator.py"]
