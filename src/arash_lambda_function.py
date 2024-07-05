import boto3
import cv2
import numpy as np
import base64
from io import BytesIO

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ObjectDetectionResults')

def detect_objects(image_bytes):
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    labels = open("coco.names").read().strip().split("\n")

    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
    height, width, channels = image.shape

    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    result = []
    for i in indices:
        i = i[0]
        box = boxes[i]
        result.append({
            "label": labels[class_ids[i]],
            "accuracy": confidences[i]
        })

    return result

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    objects = detect_objects(image_bytes)
    s3_url = f"s3://{bucket}/{key}"

    table.put_item(
        Item={
            'ImageID': key,
            'DetectedObjects': objects,
            'ImageURL': s3_url
        }
    )

    return {
        'statusCode': 200,
        'body': objects
    }
