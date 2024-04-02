#!/bin/bash

timestamp=$(date +%d--%H-%M-%S)
python3 src/mr_runner.py data/reviews_devset.json > ./logs/output_${timestamp}.txt