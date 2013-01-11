Experiments to Improve Coder Quality in Mechanical Turk 
========================================================

>  - *Last updated*: January 7, 2013
>  - *Author*: Drew Conway
>  - *Contact*: drew.conway@nyu.edu

The following repository is a collection of code, data, and web frameworks for experiments to enhance coder quality in Mechanical Turk jobs.  These experiments will generate data to be used in a paper treatment of this study.

These results will additionally be reported in a larger, co-authored, paper on using crowd-source to code political text.

**NOTE**: These files have been exposed primarily to provide replication resources for these experiments. These experiments rely on formatted web pages hosted remotely on Amazon's S3 storage service.  As such, this repository is not an "out-of-the-box" resources for generating these experiments.  The files contained on the `html`, `js`,`css`, and `data` folders must be hosted, and appropriately integrated, in order to replicate these experiments exactly.

## Experimental Design

**NOTE**: For details on the specific coding tasks please see the [worker instruction page](http://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/instructions.html).

This set of experiments seeks to test how various mechanism for qualifying Mechanical Turk workers for a text coding task can improve the quality of results.  In this experiment I use a Qualification Test data structure as the primary filtering mechanism.  Workers must pass this test in order to be qualified to work on the coding task, and thus receive compensation. 

The experiment has a two-way design, in which two variables of the qualification test are manipulated to form a comparative data set.  

 - `count`: This manipulation is the total number of sentences contained in a qualification test.  Based on the experimental design, this value must be from the following set: `{4,8,12,16}`

 - `tol`: Short for tolerance, this manipulation is how many incorrect codings -- as a percent of the total number of sentences in the qualification test -- a worker is allowed to submit and still be qualified to work on the task.   Based on the experimental design, this value must be from the following set: `{50,60,70,80}`.

### Generating an experiment

The file `data/generate_coding_data.R` and `generate_json_files.R` are both `R` scripts that will regenerate the sentence data used to create both the sentences for all of the qualifying.  The `generate_coding_data.R` file creates a set of CSV files that divides the base data set by policy area and direction.  The `generate_json_files.R` uses these data set to generate the JSON files that are then used to populate the qualification tests and coding tasks.

*Requirements*
 - Python >= 2.7
 - Amazon Web Services account with a Mechanical Turk account

The file `mturk/boto/generate_hit.py` is used to create a single experiment based on our the two-way design.  This file should be run from the command line, which contains the following help output:

	$ python generate_hit.py -h
	usage: generate_hit.py [-h] [--hits N] [--asgn N] [--count {6,12}]
	                       [--tol {67,84}] [--prod {y,n}] [--master {y,n}]

	This script will push a new experiment to MTurk. Several users defined
	arguments are required.

	optional arguments:
	  -h, --help      show this help message and exit
	  --hits N        The number of HITs to push of this type. Default is 100.
	  --asgn N        The number of assignments for each HIT. Default is 5.
	  --count {6,12}  The number of sentences in the qualification test. Default
	                  is 6.
	  --tol {67,84}   The percentage of sentences coded correctly in order to pass
	                  qualification test. Default is 67.
	  --prod {y,n}    Should this HIT be pushed to the production server? Default
	                  is 'n'.
	  --master {y,n}  Should the Master Categorization Qualification be added to
	                  this HIT? Default is 'n'.


This script automatically creates both the a new Qualification Type based on the set manipulation, and a given set of HITs linked to that qualification type.  The qualification type's title is a reference to the manipulation, as *Qualification test #`count`+(`tol` / 100)*, such that if `count`=4 and `tol`=50 the qualification title will be *Qualification test #4.5*.

The qualification test asks the worker to code example sentences pulled directly from the full sentence data set.  The formatting of the qualification test is slightly different from the coding task.  This is because the qualification test must conform to MTurk's specific data format, while the coding task is hosted externally and is thus highly customizable.

#### Qualification test screen shot

![Qualification test screen shot](http://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/qual.png)

#### Coding Task screen shot

![Coding Task screen shot](http://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/task.png)

#### Approving results and collecting data

The file `mturk/boto/approver.py` is a simple Python script that is used to download coder data, and automatically approve this work so workers can get compensated.  Work is automatically approved because all workers must first gain qualification before they are allowed to work on a given task. Once this is passed, all work is accepted.  

This file is run as a CRON job once the experiments are posted in order to most efficiently collect the data and pay workers.


## Sentence Data

At present, none of the sentence data used in these experiments is provided in this repository because the experiments are ongoing. To avoid any possible contamination of the experimental design, this data has been withheld.  Once the experimentation has been completed, all data will be made available.


