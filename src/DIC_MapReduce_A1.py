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
                            

    def combiner(self, key, values):
        yield (key, sum(values))

    def reducer(self, key, values):
        yield (key, sum(values))

    def steps(self):
        return [
            MRStep(
                mapper=self.mapper,
                combiner=self.combiner,
                reducer=self.reducer,
            )
        ]
