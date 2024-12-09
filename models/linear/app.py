from flask import Flask, request, jsonify
import joblib
import prometheus_client
from prometheus_client import Counter

# Load model
model = joblib.load("linear_regression.pkl")

# Initialize Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('linear_reg_model_requests', 'Number of requests to the Linear Regression model')

@app.route('/predict', methods=['POST'])
def predict():
    REQUEST_COUNT.inc()
    data = request.json
    features = data.get("features")
    if features:
        prediction = model.predict([features]).tolist()
        return jsonify({"prediction": prediction})
    return jsonify({"error": "Invalid input"}), 400

@app.route('/metrics', methods=['GET'])
def metrics():
    return prometheus_client.generate_latest(), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
