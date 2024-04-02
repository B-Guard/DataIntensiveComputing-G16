#!/bin/bash


# ATENTION!!
# The script executes the MRJobs on the full dataset instead of the devset.
python src/mr_runner.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop hdfs:///user/dic24_shared/amazon-reviews/full/reviewscombined.json