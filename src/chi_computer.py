#!/usr/bin/env python3

import os
import re
import heapq
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
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

STEM = True


def load_file_as_set(file: str) -> set:
    contents = set()
    with open(file, "r") as file:
        for word in file:
            contents.add(word.strip())
    return contents


def compute_chi(
    N: int, A: int, B: int, C: int, D: int
) -> float:
    try:
        return N * (A * D - B * C) ** 2 / ((A + C) * (B + D) * (A + B) * (C + D))
    except ZeroDivisionError:
        return 0.0

class ChiSquare(MRJob):

    K = 75

    INPUT_PROTOCOL = JSONValueProtocol

    def load(self):
        # Load stopwords and categories
        self.stopwords = frozenset(load_file_as_set("stopwords.txt"))
        self.categories = frozenset(load_file_as_set("category_set.txt"))
        # Main data structure to store ABCD
        self.cat_word_chi = dict()
        # Initialize the stemmer, useful later
        self.stemmer = PorterStemmer()
        # And a map to store stemmed words
        self.stemmed_words = dict()
        # Keep track of processed documents
        self.total_docs = 0

    def process_line(self, json_line):
        ### Preprocessing
        # Get review text and category. The review text is already case folded here
        review_text = json_line["reviewText"].lower()
        category = json_line["category"]

        # Tokenization to unigrams using delimiters
        pattern = r"[ \t0-9\(\)\[\]\{\}\.\!\?,;:\+=\-_\"'`~#@&%*%€$§\\/|<>^]+"
        # Converting to set to count documents instead of words
        review_words = set(re.split(pattern, review_text)) - set("")

        # Removing stopwords
        review_words = review_words - self.stopwords
        # Stemming
        condensed_review_words = set()
        if STEM:
            for w in review_words:
                if w not in self.stemmed_words.keys():
                    self.stemmed_words[w] = self.stemmer.stem(w)
                condensed_review_words.add(self.stemmed_words[w])
            return category, condensed_review_words - set("")
        else:
            return category, review_words - set("")

    def mapper(self, _, line):
        # Get category and words in document (review)
        category, words = self.process_line(line)

        # Add word to category and update its AB values
        for cat in self.categories:
            if cat not in self.cat_word_chi.keys():
                self.cat_word_chi[cat] = {"N": 0}
            for word in words:
                if word not in self.cat_word_chi[cat].keys():
                    self.cat_word_chi[cat][word] = {"A": 0, "B": 0}
                if category == cat:  # same category
                    self.cat_word_chi[cat][word]["A"] += 1  # +1 doc where t appears
                else:  # different category
                    self.cat_word_chi[cat][word]["B"] += 1  # +1 doc where t appears

        # +1 document for this category
        self.cat_word_chi[category]["N"] += 1
        # +1 document in total
        self.total_docs += 1

    def mapper_final(self):
        # Calculate C and D values for each word in each category
        for cat in self.cat_word_chi.keys():
            n = self.cat_word_chi[cat]["N"]
            for word in self.cat_word_chi[cat].keys() - set("N"):
                w = self.cat_word_chi[cat][word]
                # C is the number of documents in the category that do not contain the word
                w["C"] = n - w["A"]
                # D is the number of documents not in the category that do not contain the word
                # Or what's the same, the total number of docs minus A, B and C
                w["D"] = self.total_docs - w["C"] - w["A"] - w["B"]
                yield (cat, (word, w))

    def combiner(self, cat, w_abcd):
        aggregated_words = dict()
        # Aggregate all words and their ABCD values
        for word, abcd in w_abcd:
            if word not in aggregated_words.keys():
                aggregated_words[word] = abcd
            else:
                aggregated_words[word]["A"] += abcd["A"]
                aggregated_words[word]["B"] += abcd["B"]
                aggregated_words[word]["C"] += abcd["C"]
                aggregated_words[word]["D"] += abcd["D"]
        for word in aggregated_words.keys():
            yield (cat, (word, aggregated_words[word]))

    def reducer(self, cat, w_abcd):
        aggregated_words = dict()
        # Aggregate all words and their ABCD values
        for word, abcd in w_abcd:
            if word not in aggregated_words.keys():
                aggregated_words[word] = abcd
            else:
                aggregated_words[word]["A"] += abcd["A"]
                aggregated_words[word]["B"] += abcd["B"]
                aggregated_words[word]["C"] += abcd["C"]
                aggregated_words[word]["D"] += abcd["D"]
        # Each reducer task receives a category and a list of words with their ABCD values
        # heapq
        chis = []
        # Compute chi-square values for each word
        for word, abcd in aggregated_words.items():
            # N is the total number of documents, which can be retrieved from any word like so
            A, B, C, D = abcd["A"], abcd["B"], abcd["C"], abcd["D"]
            N = A + B + C + D

            if len(chis) < self.K:
                heapq.heappush(chis, (compute_chi(N, A, B, C, D), word))
            else:
                heapq.heappushpop(chis, (compute_chi(N, A, B, C, D), word))

        # Retrieve top K words with highest chi-square values
        top_words = {word: chi for chi, word in heapq.nlargest(self.K, chis)}
        yield cat, top_words

    def steps(self):
        return [
            MRStep(
                mapper_init=self.load,
                mapper=self.mapper,
                mapper_final=self.mapper_final,
                combiner=self.combiner,
                reducer=self.reducer,
            )
        ]


if __name__ == "__main__":
    ChiSquare().run()
