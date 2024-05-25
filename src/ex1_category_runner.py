#!/usr/bin/env python3

from ex1_category_counter import CategoryCounter
if __name__ == '__main__':
    
    job = CategoryCounter()
    with job.make_runner() as runner:
        runner.run()
        
        for key, value in job.parse_output(runner.cat_output()):           
            print(value)