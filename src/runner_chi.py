import json
from chi_computer import ChiSquare

if __name__ == "__main__":

    job = ChiSquare()
    with job.make_runner() as runner:
        runner.run()

        for key, value in job.parse_output(runner.cat_output()):
            string = f"<{key}> "
            for word in value.keys():
                string += f"{word}:{value[word]} "
            print(string)