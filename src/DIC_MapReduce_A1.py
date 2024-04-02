#!/usr/bin/env python3

import os
import re
import json
from mrjob.job import MRJob
from mrjob.step import MRStep
from nltk.stem.porter import *

### Exercise requirements:
"""
As a preparation step for text classification, we want to select
terms that discriminate well between categories.
        
Write MapReduce jobs that calculate chi-square values for the terms
in the review dataset
        
For preprocessing, make sure to perform the following steps:
- Tokenization to unigrams, using whitespaces, tabs, digits, and
the characters ()[]{}.!?,;:+=-_"'`~#@&*%€$§\/ as delimiters
- Case folding
- Stopword filtering: use the stop word list (stopwords.txt)
        
In addition, filter out all tokens consisting of only one character
        
Write MapReduce jobs that efficiently:
- Calculate chi-square values for all unigram terms for each category
- Order the terms according to their value per category and preserve
the top 75 terms per category
- Merge the lists over all categories
"""


class CategoryWordCounter(MRJob):

    def mapper(self, _, line):
        # Parse JSON line to Python dictionary
        json_line = json.loads(line)
        # Get review text and category. The review text is already case folded here
        review_text = json_line["reviewText"].lower()
        category = json_line["category"]
        # Initialize the Porter stemmer, useful later
        stemmer = PorterStemmer()

        # Load stopwords from file
        stopwords = set()
        stopwords_file = os.path.join(os.path.dirname(__file__), "../data/stopwords.txt")
        with open(stopwords_file, "r") as file:
            for word in file:
                stopwords.add(word.strip())

        # Tokenization to unigrams using delimiters
        pattern = r"[ \t0-9\(\)\[\]\{\}\.\!\?,;:\+=\-_\"'`~#@&*%€$§\\/|<>^]+"
        review_words = re.split(pattern, review_text)

        # Stopword filtering and stemming words
        review_words = [
            stemmer.stem(word) # With stemming, we get around 70000 ngrams
            # word # Without stemming, we get around 100000 ngrams
            for word in review_words
            if len(word) > 1 and word not in stopwords
        ]

        # Set to remember if a (category, word) pair has already been yielded
        # This allows to only count corpuses instead of individual words
        yielded_keys = set()
        
        for word in review_words:
            if (category, word) not in yielded_keys:
                yielded_keys.add((category, word))
                yield ((category,word), 1)
                            

    def combiner(self, category_word, values):
        yield (category_word, sum(values))

    def reducer(self, category_word, values):
        category, word = category_word
        yield (category, {word: sum(values)})

    def reducer_aggregate(self, category, word_counts):
        word_count_dict = {}
        for wc in word_counts:
            word_count_dict.update(wc)

        # Yield the category and the combined word count dictionary
        yield category, word_count_dict

    def steps(self):
        return [
            MRStep(
                mapper=self.mapper,
                combiner=self.combiner,
                reducer=self.reducer
            ),
            MRStep(
                reducer=self.reducer_aggregate
            )
        ]


"""
Configuration yarn.app.mapreduce.am.resource.memory-mb=8192Mi is overriding the yarn.app.mapreduce.am.resource.mb=1536 configuration
  Job not successful!

Probable cause of failure:

Error: java.io.IOException: Broken pipe
	at java.io.FileOutputStream.writeBytes(Native Method)
	at java.io.FileOutputStream.write(FileOutputStream.java:326)
	at java.io.BufferedOutputStream.write(BufferedOutputStream.java:122)
	at java.io.BufferedOutputStream.flushBuffer(BufferedOutputStream.java:82)
	at java.io.BufferedOutputStream.write(BufferedOutputStream.java:126)
	at java.io.DataOutputStream.write(DataOutputStream.java:107)
	at org.apache.hadoop.streaming.io.TextInputWriter.writeUTF8(TextInputWriter.java:72)
	at org.apache.hadoop.streaming.io.TextInputWriter.writeValue(TextInputWriter.java:51)
	at org.apache.hadoop.streaming.PipeMapper.map(PipeMapper.java:106)
	at org.apache.hadoop.mapred.MapRunner.run(MapRunner.java:54)
	at org.apache.hadoop.streaming.PipeMapRunner.run(PipeMapRunner.java:34)
	at org.apache.hadoop.mapred.MapTask.runOldMapper(MapTask.java:466)
	at org.apache.hadoop.mapred.MapTask.run(MapTask.java:350)
	at org.apache.hadoop.mapred.YarnChild$2.run(YarnChild.java:178)
	at java.security.AccessController.doPrivileged(Native Method)
	at javax.security.auth.Subject.doAs(Subject.java:422)
	at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1899)
	at org.apache.hadoop.mapred.YarnChild.main(YarnChild.java:172)


Traceback (most recent call last):
  File "/home/dic24/e***/Exercise_1/src/mr_runner.py", line 12, in <module>
    runner.run()
  File "/sw/venv/python39/dic24/lib/python3.9/site-packages/mrjob/runner.py", line 503, in run
    self._run()
  File "/sw/venv/python39/dic24/lib/python3.9/site-packages/mrjob/hadoop.py", line 329, in _run
    self._run_job_in_hadoop()
  File "/sw/venv/python39/dic24/lib/python3.9/site-packages/mrjob/hadoop.py", line 405, in _run_job_in_hadoop
    raise StepFailedException(
mrjob.step.StepFailedException: Step 1 of 1 failed: Command '['/usr/bin/hadoop', 'jar', '/usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.5.jar', '-files', 'hdfs:///user/e***/tmp/mrjob/DIC_MapReduce_A1.e***.20240402.084548.134877/files/wd/DIC_MapReduce_A1.py#DIC_MapReduce_A1.py,hdfs:///user/e***/tmp/mrjob/DIC_MapReduce_A1.e***.20240402.084548.134877/files/wd/mrjob.zip#mrjob.zip,hdfs:///user/e***/tmp/mrjob/DIC_MapReduce_A1.e***.20240402.084548.134877/files/wd/setup-wrapper.sh#setup-wrapper.sh', '-cmdenv', 'TZ=Europe/Vienna', '-input', 'hdfs:///user/dic24_shared/amazon-reviews/full/reviews_devset.json', '-output', 'hdfs:///user/e***/tmp/mrjob/DIC_MapReduce_A1.e***.20240402.084548.134877/output', '-mapper', '/bin/sh -ex setup-wrapper.sh /sw/venv/python39/dic24/bin/python DIC_MapReduce_A1.py --step-num=0 --mapper', '-combiner', '/bin/sh -ex setup-wrapper.sh /sw/venv/python39/dic24/bin/python DIC_MapReduce_A1.py --step-num=0 --combiner', '-reducer', '/bin/sh -ex setup-wrapper.sh /sw/venv/python39/dic24/bin/python DIC_MapReduce_A1.py --step-num=0 --reducer']' returned non-zero exit status 256.
"""
