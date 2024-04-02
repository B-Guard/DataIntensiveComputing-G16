#!/usr/bin/env python

import sys
import json

from DIC_MapReduce_A1 import *

if __name__ == "__main__":

    job = CategoryWordCounter()
    top_k = 75  # Number of top words to keep per category
    with job.make_runner() as runner:
        runner.run()
        output = {}
        for key, value in job.parse_output(runner.cat_output()):
            output[key] = value

    # Set to store all words
    all_words = set()

    # Calculate the total number of documents (N)
    N = sum(sum(word_counts.values()) for word_counts in output.values())

    # Dictionary to store the chi-square values for each word in each category
    chi_square_values = {
        category: {word: 0 for word in word_counts}
        for category, word_counts in output.items()
    }

    # Calculate the chi-square values for each word in each category
    for category, word_counts in output.items():
        for word, count in word_counts.items():
            # Add the word to the set of all words
            all_words.add(word)
            # Compute the chi-square value for the word in the category
            A = count  # A is already provided by the MR job
            B = sum(  # B is the sum of the word counts in all other categories
                word_counts.get(
                    word, 0
                )  # By default, the count is 0 if the word is not found
                for cat, word_counts in output.items()
                if cat != category
            )
            C = (
                sum(word_counts.values()) - A
            )  # C is the sum of the word counts in the category
            D = N - A - B - C  # D is the sum of the word counts in all other categories
            chi_square = (
                N * (A * D - B * C) ** 2 / ((A + C) * (B + D) * (A + B) * (C + D))
            )
            chi_square_values[category][word] = chi_square

    # Sort the chi-square values in descending order and get the top K for each category
    for category, word_chi_squares in chi_square_values.items():
        sorted_word_chi_squares = sorted(
            word_chi_squares.items(), key=lambda item: item[1], reverse=True
        )
        tops = sorted_word_chi_squares[:top_k]
        chi_square_values[category] = dict(tops)

    # Write the chi_square_values to a file
    with open("output.txt", "w") as f:
        for category, word_chi_squares in chi_square_values.items():
            line = (
                category
                + " "
                + " ".join(
                    f"{word}:{chi_square}"
                    for word, chi_square in word_chi_squares.items()
                )
            )
            f.write(line + "\n")
        # f.write(" ".join(sorted(all_words)) + "\n")
