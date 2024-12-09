from flask import Flask, request, jsonify
from transformers import AutoProcessor, AutoModelForImageClassification
import torch
from PIL import Image
import prometheus_client
from prometheus_client import Counter

# Load model
processor = AutoProcessor.from_pretrained("microsoft/resnet-50")
image_model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")

# Initialize Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('image_model_requests', 'Number of requests to the Image Classification model')

@app.route('/predict', methods=['POST'])
def predict():
    with open('debug.txt', 'a') as f:#############################
        #f.write("Predicting\n") ##############
        REQUEST_COUNT.inc()
        try:
            data = request.json
            image_path = data.get("image_path")
            #f.write(f"Image path: {image_path}\n") ##############
            if image_path:
                image = Image.open(image_path).convert("RGB")  # Open the image directly from the path
                inputs = processor(images=image, return_tensors="pt")
                outputs = image_model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = probs.argmax().item()
                return jsonify({
                    "class": image_model.config.id2label[predicted_class],
                    "confidence": probs.max().item()
                })
            #f.write(f"No image path received\n") ##############
            return jsonify({"error": "Invalid input"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    return prometheus_client.generate_latest(), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
