#!/usr/bin/env python3

import re
import json
from mrjob.job import MRJob
from mrjob.step import MRStep

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
- Stopword filtering</strong>: use the stop word list (stopwords.txt)
        
In addition, filter out all tokens consisting of only one character
        
Write MapReduce jobs that efficiently:
- Calculate chi-square values for all unigram terms for each category
- Order the terms according to their value per category and preserve
the top 75 terms per category
- Merge the lists over all categories
"""


class WordCount(MRJob):

    def mapper(self, _, line):
        json_line = json.loads(line)
        review_text = json_line["reviewText"]

        # This line needs a fix, there are too many ngrams coming out of the filter
        review_words = re.findall(r"\b\w+\b", review_text.lower())

        for word in review_words:
            yield (word, 1)

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
