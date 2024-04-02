# Data Intensive Computing
## Group 16

### Exercise 1
[Exercise 1 sheet](./exercise_sheets/ex1.html)

#### Execution
Three different bash scripts have been added to help speed up development.
If you want to run the job locally, call:
```bash
./local_runner.sh
```
If instead wanting to test on the cluster, run either of the following:
```bash
./cluster_runner.sh

# Caution, this will run the jobs on the full dataset
./full_cluster_runner.sh
```

Remember to give execution rights with:
```bash
sudo chmod +x local_runner.py
sudo chmod +x cluster_runner.py
sudo chmod +x full_cluster_runner.py
```

#### Action plan
The ultimate goal is to compute chi-squared values. To do so according to literature, 5 different metrics need to be counted. 
These are:
- **A**: number of documents in corpus C which contain term T
- **B**: number of documents not in corpus C which contain term T
- **C**: number of documents in corpus C which do not contain term T
- **D**: number of documents not in corpus C which do not contain term T
- **N**: total number of documents in corpus C

Note that, with *corpus C*, we refer to the corpus of a specific category.
That is, all reviews in the dataset that belong to that category.

The question now is to come up with clever MapReduce jobs that count these metrics efficiently.

Regardless on how many MapReduce jobs are implement, all of them must preprocess the date in the same way. That is, they must:
- Tokenize to unigrams
- Fold cases
- Filter out stopwords
- Filter out tokens consisting of only one character
