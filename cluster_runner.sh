#!/bin/bash


# Runner script for running the hadoop job on the cluster
# Uses the small dataset for testing
python3 src/mr_runner.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop hdfs:///user/dic24_shared/amazon-reviews/full/reviews_devset.json > ./logs/output_$(date +%d--%H-%M-%S).txt
