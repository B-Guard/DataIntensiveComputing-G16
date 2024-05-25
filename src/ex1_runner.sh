#!/bin/bash

# Automatic cluster runner, to execute the whole pipeline
# This script should be executed from the root directory of this project

if [ "$1" = "-f" ]; then
    echo "Running on full dataset"
    file="reviewscombined.json"
else 
    echo "Running on devel set (pass -f to run on full dataset)"
    file="reviews_devset.json"
fi
echo "MRJob 1/2: creating category set"
python3 category_runner.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop hdfs:///user/dic24_shared/amazon-reviews/full/$file > ../data/category_set.txt
echo "MRJob 2/2: computing chi-squares"
time python3 runner_chi.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop --files=../data/stopwords.txt,../data/category_set.txt hdfs:///user/dic24_shared/amazon-reviews/full/$file > output.txt
