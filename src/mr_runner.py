#!/usr/bin/env python

import sys
import json

from DIC_MapReduce_A1 import *

if __name__ == "__main__":

    myjob1 = WordCount()
    with myjob1.make_runner() as runner:
        runner.run()

        for key, value in myjob1.parse_output(runner.cat_output()):
            print(key, value, "\n", end="")
