from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import os


# Load YOLO model
def load_yolo():
    net = cv2.dnn.readNet(
        os.path.join("yolo_tiny_configs", "yolov3-tiny.weights"),
        os.path.join("yolo_tiny_configs", "yolov3-tiny.cfg"),
    )
    with open(os.path.join("yolo_tiny_configs", "coco.names"), "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes


# Detect objects in the image
def detect_objects(net, classes, image):
    # Network does not accept raw images, they need to be preprocessed first into blobs
    # This implies:
    # - Resizing
    # - Channel scaling (1/255~=0.00392) and mean centering (not done here)
    # - Channel reordering (from BGR to RGB)
    blob = cv2.dnn.blobFromImage(
        image, 1/255, (416, 416), (0, 0, 0), True, crop=False
    )
    net.setInput(blob)
    outs = net.forward(
        [net.getLayerNames()[i - 1] for i in net.getUnconnectedOutLayers()]
    )

    results = []

    # Extract class IDs and confidences from detections
    for out in outs:
        for detection in out:
            scores = detection[5:]  # Ignore the first 5 values (box coordinates)
            class_id = np.argmax(scores)
            confidence = float(scores[class_id])
            if confidence > 0.5:  # Confidence threshold
                label = str(classes[class_id])
                results.append({"label": label, "accuracy": confidence})
    return results

app = Flask(__name__)
net, classes = load_yolo()


@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()
        image_id = data["id"]
        image_data = data["image"]

        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Detect objects
        objects = detect_objects(net, classes, image)

        # Create response
        response = {"id": image_id, "objects": objects}
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
