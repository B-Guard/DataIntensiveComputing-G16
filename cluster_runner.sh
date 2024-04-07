#!/bin/bash


# Dev set
python3 src/runner_chi.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop --files=./data/stopwords.txt,./data/category_set.txt hdfs:///user/dic24_shared/amazon-reviews/full/reviews_devset.json > ./results/devset.txt

# Full data set
python3 src/runner_chi.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop --files=./data/stopwords.txt,./data/category_set.txt hdfs:///user/dic24_shared/amazon-reviews/full/reviewscombined.json > ./results/full.txt
