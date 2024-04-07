#!/bin/bash
timestamp=$(date +%d--%H-%M)
time python3 src/chi_computer.py data/reviews_devset.json --files=data/stopwords.txt,data/category_set.txt > ./logs/output_${timestamp}.txt