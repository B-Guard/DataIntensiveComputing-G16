#!/bin/bash
timestamp=$(date +%d--%H-%M)
python3 src/runner_chi.py data/reviews_devset.json --files=data/stopwords.txt,data/category_set.txt > ./logs/output_${timestamp}.txt