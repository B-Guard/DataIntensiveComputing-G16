#!/usr/bin/env python3

from ex1_chi_computer import ChiSquare

if __name__ == "__main__":

    job = ChiSquare()
    set_of_words = set()
    with job.make_runner() as runner:
        runner.run()

        categories = dict()
        for key, value in job.parse_output(runner.cat_output()):
            categories[key] = value
            for word in value.keys():
                set_of_words.add(word)
        
        categories = sorted(categories.items(), key=lambda x: x[0])
        set_of_words = sorted(list(set_of_words))
        for cat, words in categories:
            print(cat, end="")
            for word in words.items():
                print(f" {word[0]}:{word[1]}", end="")
            print()
        [print(w, end=" ") for w in set_of_words]