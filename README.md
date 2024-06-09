# Data Intensive Computing
## Group 16

### Exercise 1
[Exercise 1 sheet](./exercise_sheets/ex1.html)

#### Execution
How to run the code?
Before running anything, be aware that the [Chi square computer](./src/chi_computer.py) script needs two helper files, namely: [stopwords.txt](./data/stopwords.txt), which is already provided, and [category_set.txt](), which needs to be generated beforehand. Have a look at [category_runner.sh](category_runner.sh) and choose the command appropiate to your case.

You can choose between running locally and running on the cluster. The commands needed for either are provided in these two files:
```bash
local_runner.sh

cluster_runner.sh
```
If developing locally, you can opt to give execution rights to `local_runner.sh` to speed up execution. On the cluster, since we do not have admin rights, this is not possible.


#### Action plan
The ultimate goal is to compute chi-squared values. To do so according to literature, 5 different metrics need to be counted. 
These are:
- **A**: number of documents in corpus C which contain term T
- **B**: number of documents not in corpus C which contain term T
- **C**: number of documents in corpus C which do not contain term T
- **D**: number of documents not in corpus C which do not contain term T
- **N**: total number of retrieved documents


Note that, with *corpus C*, we refer to the corpus of a specific category.
That is, all reviews in the dataset that belong to that category.

Preprocessing tasks for every document:
- Tokenize to unigrams
- Fold cases
- Filter out stopwords
- Filter out tokens consisting of only one character
- *Additional spice added by us*: stem words


### Exercise 2
[Exercise sheet](exercise_sheets/ex2.html)

### Exercise 3

[Exercise sheet](exercise_sheets/Exercise%203_2024S.pdf)

#### Local execution
Some dependencies are needed for this project. Install them with `pip install -r requirements.txt`.

For the server to run properly, you need the YOLO model weights in the appropiate location. The script expects to find them under the folder [yolo_tiny_configs](/yolo_tiny_configs/), which is already provided in this repo.
To get the server running, execute `python src/ex3_local_server.py`. After this, you should be ready to execute `python src/ex3_client.py <input_folder> http://localhost:5000/upload`, where `<input_folder>` is the location of your test images.