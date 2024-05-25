#!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol

class CategoryCounter(MRJob):

    INPUT_PROTOCOL = JSONValueProtocol

    def line_processor(self, _, line):
        yield None, line["category"]

    def reducer(self, _, words):
        cat_set = set(words)
        for cat in cat_set:
            yield None, cat

    def steps(self):
        return [
            MRStep(
                mapper=self.line_processor,
                reducer=self.reducer
            )
        ]

if __name__ == "__main__":
    CategoryCounter().run()