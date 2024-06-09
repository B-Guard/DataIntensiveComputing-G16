import base64
import requests
import uuid
import json
import os
import sys
from pathlib import Path
import psutil
import time
import argparse

parser = argparse.ArgumentParser(description='Process images and send them to a server.')
parser.add_argument('input_folder', type=str, help='The input folder containing images to process.')
parser.add_argument('server_url', type=str, help='The server URL to send processed images to.')
parser.add_argument('--save', action='store_true', help='Save the processed images locally.')
parser.add_argument('--print', action='store_true', help='Print the response for each image.')

# Parse arguments
args = parser.parse_args()

# Use the flags from arguments
SAVE = args.save
PRINT = args.print

# Create logs folder
def create_logs_folder():
    if not os.path.exists("logs"):
        os.makedirs("logs")


# Encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


# Post image to server and process response
def post_image(image_path, server_url, log_filename):
    image_id = str(uuid.uuid4())  # Generate unique ID for the image
    encoded_image = encode_image(image_path)  # Encode the image
    payload = {"id": image_id, "image": encoded_image}  # Create the payload

    try:
        response = requests.post(server_url, json=payload)  # Send the POST request

        # Process the response
        if response.status_code == 200:
            response_data = response.json()
            if PRINT:
                print(f"Response for image {image_path}:")
                print(json.dumps(response_data, indent=1))

            # Append the response to a single log file
            if SAVE:
                result = {
                    "image_name": os.path.basename(image_path),
                    "uuid": image_id,
                    "objects": response_data["objects"],
                }            
                append_to_log(log_filename, result)
        else:
            print(
                f"Failed to get a response for image {image_path}, status code: {response.status_code}"
            )
            print(response.json())
    except Exception as e:
        print(f"An error occurred while processing image {image_path}: {e}")


# Append data to log file
def append_to_log(log_filename, data):
    if not os.path.exists(log_filename):
        with open(log_filename, "w") as log_file:
            json.dump({"results": [data]}, log_file, indent=1)
    else:
        with open(log_filename, "r+") as log_file:
            log_data = json.load(log_file)
            log_data["results"].append(data)
            log_file.seek(0)
            json.dump(log_data, log_file, indent=1)


if __name__ == "__main__":
    if not os.path.isdir(args.input_folder):
        print(f"The input folder {args.input_folder} does not exist.")
        sys.exit(1)

    input_folder = sys.argv[1]
    server_url = sys.argv[2]

    # Check if the input folder exists
    if not os.path.isdir(input_folder):
        print(f"The input folder {input_folder} does not exist.")
        sys.exit(1)

    # Create logs folder and log filename
    create_logs_folder()
    log_filename = f'logs/localYOLO.json'

    # Start benchmark
    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_cpu_times = process.cpu_times()

    # Process each image in the input folder
    for image_file in Path(input_folder).glob("*.*"):
        if image_file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            post_image(str(image_file), server_url, log_filename)
    
    # End benchmark
    end_time = time.time()
    cpu_usage_end = process.cpu_percent(interval=None)
    end_cpu_times = process.cpu_times()

    # Calculate and print benchmark results
    total_time = end_time - start_time
    user_time = end_cpu_times.user - start_cpu_times.user
    system_time = end_cpu_times.system - start_cpu_times.system


    print(f"\nBenchmark Results:")
    print(f"\tTotal time taken: {total_time:.2f} seconds")
    print(f"\tUser CPU time: {user_time:.2f} seconds")
    print(f"\tSystem CPU time: {system_time:.2f} seconds")

