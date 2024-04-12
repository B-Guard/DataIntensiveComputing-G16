#!/usr/bin/env python3

from chi_computer import ChiSquare

if __name__ == "__main__":

    job = ChiSquare()
    set_of_words = set()
    with job.make_runner() as runner:
        runner.run()

        for key, value in job.parse_output(runner.cat_output()):
            string = f"<{key}> "
            for word in value.keys():
                string += f"{word}:{value[word]} "
                set_of_words.add(word)
            print(string)
        set_of_words = sorted(list(set_of_words))
        [print(w, end=" ") for w in set_of_words]