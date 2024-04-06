#!/usr/bin/env python3
import json
from mrjob.job import MRJob
from mrjob.step import MRStep

class CategoryCounter(MRJob):

    def line_processor(self, _, line):
        yield None, json.loads(line)["category"]

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