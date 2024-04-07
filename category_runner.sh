
# Locally
python3 src/category_runner.py ./data/reviews_devset.json > ./data/category_set.txt

# Cluster
# Dev set
python3 src/category_runner.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop hdfs:///user/dic24_shared/amazon-reviews/full/reviews_devset.json > ./data/category_set.txt

# Full data set
python3 src/category_runner.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -r hadoop hdfs:///user/dic24_shared/amazon-reviews/full/reviewscombined.json > ./data/category_set.txt