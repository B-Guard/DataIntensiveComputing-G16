import boto3
import base64
import cv2
import numpy as np
import os
import logging


# Load YOLO model
def load_yolo():
    net = cv2.dnn.readNet(
        os.path.join("/tmp", "yolov3-tiny.weights"),
        os.path.join("/tmp", "yolov3-tiny.cfg"),
    )
    with open(os.path.join("/tmp", "coco.names"), "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes


# Detect objects in the image
def detect_objects(net, classes, image):
    blob = cv2.dnn.blobFromImage(
        image, 1 / 255, (416, 416), (0, 0, 0), True, crop=False
    )
    net.setInput(blob)
    outs = net.forward(
        [net.getLayerNames()[i - 1] for i in net.getUnconnectedOutLayers()]
    )

    results = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = float(scores[class_id])
            if confidence > 0.5:
                label = str(classes[class_id])
                results.append({"label": label, "accuracy": confidence})
    return results


# Initialize YOLO model
net, classes = load_yolo()


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table_name = os.getenv('DYNAMODB_TABLE_NAME')
    table = dynamodb.Table(table_name)

    try:
        # Get bucket name and image key from the event
        bucket_name = os.getenv('S3_BUCKET_NAME')
        image_key = event['Records'][0]['s3']['object']['key']

        # Download image from S3
        s3.download_file(bucket_name, image_key, '/tmp/temp_image.jpg')

        # Read image
        image = cv2.imread('/tmp/temp_image.jpg')

        # Detect objects
        objects = detect_objects(net, classes, image)

        # Get S3 URL
        s3_url = f"s3://{bucket_name}/{image_key}"

        # Store results in DynamoDB
        response = table.put_item(
            Item={
                'image_key': image_key,
                's3_url': s3_url,
                'objects': objects
            }
        )

        # Log the results
        logging.info(f"Results: {objects}")

        return {
            'statusCode': 200,
            'body': f"Detection results stored for {image_key}"
        }
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing image: {e}"
        }
