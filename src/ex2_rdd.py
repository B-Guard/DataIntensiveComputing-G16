# Imports
from pyspark import SparkContext, SparkConf
from pyspark.rdd import RDD

import re
import json


# Create a SparkConf object
conf = SparkConf().setAppName("MyApp")

# Initialize SparkContext with the SparkConf object
sc = SparkContext(conf=conf)

# File locations
dev_set_path = "hdfs:///user/dic24_shared/amazon-reviews/full/reviews_devset.json"
full_set_path = "hdfs:///user/dic24_shared/amazon-reviews/full/reviewscombined.json"
stopwords_path = "../data/stopwords.txt"

delim = "[ \t0-9\\(\\)\\[\\]\\{\\}\\.\\!\\?,;:\\+=\\-_\"'`~#@&%*%€$§\\\\/|<>^]+"

VERBOSE = False
DEVEL = True


# Helper functions


# Print first k elements of an RDD, k default 2
# T is template parameter
def pprint(rdd: RDD, k=2):
    if VERBOSE:
        for x in rdd.take(k):
            print(x)


# Compute chi-squares by N, A, B, C
def chi_square(N: int, A: int, B: int, C: int) -> float:
    D = N - A - B - C
    num = N * ((A * D - B * C) ** 2)
    den = (A + C) * (B + D) * (A + B) * (C + D)
    if den == 0:
        return 0.0
    else:
        return num / den


# Load dataset into an RDD
dataset = sc.textFile(dev_set_path) if DEVEL else sc.textFile(full_set_path)

# Load stopwords into a set
with open(stopwords_path, "r") as f:
    stopwords = set(line.strip() for line in f)
# Add empty string. For some reason it appeared after tokenizing. This prevents it
stopwords.add("")

pprint(dataset)
print(list(stopwords)[:50])


# Parsing JSON line
# Tokenized, lowercased and stopwords removed
def parse_line(line):
    data = json.loads(line)
    category = data["category"]
    review = set(re.split(delim, data["reviewText"].lower())) - stopwords
    return (category, review)


categoryReview = dataset.map(parse_line)

pprint(categoryReview, 5)


unfolded_words = categoryReview.flatMap(lambda x: [(x[0], i) for i in x[1]])

# Obtaining the number of reviews per word
reviews_per_word = unfolded_words.map(lambda x: (x[1], 1)).reduceByKey(
    lambda x, y: x + y
)

# Obtaining the number of reviews per category
reviews_per_category = categoryReview.map(lambda x: (x[0], 1)).reduceByKey(
    lambda x, y: x + y
)

# Obtaining the total number of reviews (N) by summing up the number of reviews per category
N = reviews_per_category.map(lambda x: x[1]).reduce(lambda a, b: a + b)
print(N)
print()
pprint(reviews_per_word)
print()
pprint(reviews_per_category)

# Computing A
aValuesRDD = unfolded_words.map(lambda x: (x, 1)).reduceByKey(lambda x, y: x + y)
# Compute B values
bValuesRDD = (
    aValuesRDD.map(lambda x: (x[0][1], (x[0][0], x[1])))
    .join(reviews_per_word)
    .map(lambda x: ((x[1][0][0], x[0]), (x[1][1] - x[1][0][1])))
)
# Compute C values
cValuesRDD = (
    aValuesRDD.map(lambda x: (x[0][0], (x[0][1], x[1])))
    .join(reviews_per_category)
    .map(lambda x: ((x[0], x[1][0][0]), (x[1][1] - x[1][0][1])))
)

# Combine A, B, and C values
abcValuesRDD = (
    aValuesRDD.join(bValuesRDD)
    .join(cValuesRDD)
    .map(lambda x: ((x[0][0], x[0][1]), (x[1][0][0], x[1][0][1], x[1][1])))
)

pprint(aValuesRDD)
pprint(bValuesRDD)
pprint(cValuesRDD)
pprint(abcValuesRDD)

# Compute chi-square values
chiSquareRDD = abcValuesRDD.map(
    lambda x: ((x[0][0], x[0][1]), chi_square(N, x[1][0], x[1][1], x[1][2]))
)


# Group by category, sort by chi and retrieve top K
K = 75
topKChiSquareRDD = (
    chiSquareRDD.map(lambda x: (x[0][0], (x[0][1], x[1])))
    .groupByKey()
    .mapValues(lambda x: sorted(list(x), key=lambda y: -y[1])[:K])
)

pprint(topKChiSquareRDD)

# Format RDD as requested
outputFile = "../output_rdd.txt"
formated_result = topKChiSquareRDD.map(
    lambda x: f"{x[0]} {' '.join([f'{y[0]}:{y[1]}' for y in x[1]])}"
)
formated_result = formated_result.coalesce(1).collect()

# Get merged dictionary of terms
merged_dict = sorted(
    set(topKChiSquareRDD.flatMap(lambda x: [w[0] for w in x[1]]).distinct().collect())
)
stringified = ",".join(merged_dict)

# Save to file
with open(outputFile, "w") as f:
    for line in formated_result:
        f.write(line + "\n")
    f.write(stringified)


sc.stop()
