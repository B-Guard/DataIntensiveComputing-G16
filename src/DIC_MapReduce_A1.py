import re
import json
from mrjob.job import MRJob
from mrjob.step import MRStep

class WordCount(MRJob):

    def mapper_init(self):

        if hasattr(self, 'json_data'):
            self.data = self.json_data
        else:
            raise ValueError("JSON data not provided.")
        
    def mapper(self, _, __):
        for review in self.data:
            review_text = review['reviewText'] 
            review_words = re.findall(r"\b\w+\b",review_text.lower())

            for words in review_words:
                yield words, 1 
            
    def combiner(self, key, values):
        yield key, sum(values)

    def reducer(self, key, values):
        yield key, sum(values)

    def set_json_data(self, json_data):
        self.json_data = json_data

    def steps(self):
        return[
            MRStep(
                mapper_init = self.mapper_init,
                mapper = self.mapper,
                combiner = self.combiner, 
                reducer = self.reducer
            )
        ]

if __name__ == '__main__':
    with open("E:/Learn/Python/Amazone_Test.json", 'r') as file:
        json_data = json.load(file)

    mr_job = WordCount()
    mr_job.set_json_data(json_data)
    mr_job.run()
