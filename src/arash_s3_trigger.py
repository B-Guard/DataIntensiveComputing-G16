import boto3
import os
from base64 import b64encode

s3 = boto3.client('s3')
bucket_name = 'my-object-detection-bucket-dic-2024-2'

def upload_image(image_path):
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
        image_base64 = b64encode(image_bytes).decode('utf-8')

        s3.put_object(
            Bucket=bucket_name,
            Key=os.path.basename(image_path),
            Body=image_bytes,
            ContentType='image/jpeg'
        )

        print(f'Uploaded {image_path} to S3.')

if __name__ == "__main__":
    image_folder = 'input_folder'
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        upload_image(image_path)
