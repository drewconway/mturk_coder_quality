#!/usr/bin/env python
# encoding: utf-8
"""
generate_hit.py

Description:	A command-line interface for generating a a coder quality experiment. Hit contains a Qualification 
				test and an external questions hosted on S3.  Usage is as follows:

				$ python generate_hit.py -h
				usage: generate_hit.py [-h] [--hits N] [--asgn N] [--count {6,12}]
				                       [--tol {67,84}] [--prod {y,n}] [--master {y,n}]
				                       [--access ACCESS] [--secret SECRET]

				This script will push a new experiment to MTurk. Several users defined
				arguments are required.

				optional arguments:
				  -h, --help       show this help message and exit
				  --hits N         The number of HITs to push of this type. Default is 50.
				  --asgn N         The number of assignments for each HIT. Default is 30.
				  --count {6,12}   The number of sentences in the qualification test. Default
				                   is 6.
				  --tol {67,84}    The percentage of sentences coded correctly in order to
				                   pass qualification test. Default is 67.
				  --prod {y,n}     Should this HIT be pushed to the production server? Default
				                   is 'n'.
				  --master {y,n}   Should the Master Categorization Qualification be added to
				                   this HIT? Default is 'n'.
				  --access ACCESS  Your AWS access key. Will look for boto configuration file
				                   if nothing is provided
				  --secret SECRET  Your AWS secret access key. Will look for boto
				                   configuration file if nothing is provided

Created by  (drew.conway@nyu.edu) on
# Copyright (c) , under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, Requirement
from boto.mturk.question import ExternalQuestion
from generate_qualification import CoderQualityQualificationTest,CoderQualityQualificationType
import argparse
from datetime import datetime


if __name__ == '__main__':

	# Account data saved locally in config boto config file
	# http://code.google.com/p/boto/wiki/BotoConfig
	
	# Take in arguments provided to script by user. The first set are basic HIT components
	parser = argparse.ArgumentParser(description='This script will push a new experiment to MTurk. Several users defined arguments are required.')
	parser.add_argument("--hits", metavar="N", type=int, default=50,
		help="The number of HITs to push of this type. Default is 50.")
	parser.add_argument("--asgn", metavar="N", type=int, default=30,
		help="The number of assignments for each HIT. Default is 30.")
	
	# This is our two-way experimental design, by number of qualification sentences in test and 
	# tolerance for incorrect codings. Thus, the user inputs are restricted to those discussed
	# during the planning phase!
	parser.add_argument("--count", type=int, choices=[6,12], default=6, 
		help="The number of sentences in the qualification test. Default is 6.")
	parser.add_argument("--tol", type=int, choices=[67,84], default=67,
		help="The percentage of sentences coded correctly in order to pass qualification test. Default is 67.")
	
	# Optional components to alter HIT location and Requirement
	parser.add_argument("--prod", type=str, choices="yn", default="n",
		help="Should this HIT be pushed to the production server? Default is 'n'.")
	parser.add_argument("--master", type=str, choices="yn", default="n",
		help="Should the Master Categorization Qualification be added to this HIT? Default is 'n'.")

	# Options to set AWS credentials
	parser.add_argument("--access", type=str, default="",
		help="Your AWS access key. Will look for boto configuration file if nothing is provided")

	parser.add_argument("--secret", type=str, default="",
		help="Your AWS secret access key. Will look for boto configuration file if nothing is provided")
	
	# Get arguments from user 
	args = parser.parse_args()

	# Assign high-level values from user 
	i = args.count
	c = args.tol / 100.
	hits_to_push = args.hits
	assignments = args.asgn
	access = args.access
	secret = args.secret
	
	# Toggle production or sandbox elements
	if args.prod == "n":
		host = "mechanicalturk.sandbox.amazonaws.com"
		# Master Categorization Requirenment - sandbox
		master_req = Requirement(qualification_type_id="2F1KVCNHMVHV8E9PBUB2A4J79LU20F",
							 comparator="Exists")
	else:
		host = "mechanicalturk.amazonaws.com"
		# Master Categorization Requirenment - production
		master_req = Requirement(qualification_type_id="2NDP2L92HECWY8NS8H3CK0CP5L9GHO",
							 comparator="Exists")

	## Create qualification type

	# Where the qualification sentence data is located
	data_dir = "../../data/json/"

	## Constant info used in all qualification test
	qual_description = "A qualification test in which you read sentences from political texts and judge whether these deal with economic or social policy."
	keywords = ["text","coding","political"]
	duration = 30*60

	# Open MTurk connection
	if access != "" and secret != "":
		mturk = MTurkConnection(host = host, aws_access_key_id=access, aws_secret_access_key=secret)
	else:
		mturk = MTurkConnection(host = host)
	
	## Constant data used in all HITs
	num_hit_questions = 6
	external_url = "http://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/index.html?n="+str(num_hit_questions)
	hit_description = "This task involves reading sentences from political texts and judging whether these deal with economic or social policy."
	base_reward = 0.11
	duration = 3600
	lifetime = 259200
	# approval_delay = 86400

	# Create Question for HIT
	external_question = ExternalQuestion(external_url=external_url, frame_height=800)

	# Create HITs with qualification test
	hit_results = []
	
	# Create separate qualifications and -- HITs associated with them -- for each question set"
	title = "Qualification test #"+str(i+c)+" for recording the contents of political text on economic and social scales"
	qual_name = "Coder Qualification Test #"+str(i+c)

	# Create qualification test object.  Need to check that the qualification hasn't already been generated.
	# If it has, pull it from the set, otherwise generate it.
	current_quals = mturk.search_qualification_types(query="Coder")
	current_qual_names = map(lambda q: q.Name, current_quals)
	if qual_name not in current_qual_names:
		qual = CoderQualityQualificationTest(data_dir+"training/"+str(i)+"_"+str(int(c*100))+".json", c, title)

		# Create new qualification type
		qual_type = CoderQualityQualificationType(mturk, qual, qual_name, qual_description, keywords, duration, create=True)
		qual_id = qual_type.get_type_id()
	else:
		requested_qual = current_qual_names.index(qual_name)
		qual_type = current_quals[requested_qual]
		qual_id = qual_type.QualificationTypeId


	## Register test as a requirement for hit
	
	req = Requirement(qualification_type_id=qual_id, 
					  comparator="GreaterThan", 
					  integer_value=0)
	qual = Qualifications()
	qual.add(req)	

	# Toggle on Master Categorization from user input
	if args.master == "y":
		qual.add(master_req)	

	### Create HIT with qualification test

	# Title changes based on qualifications
	hit_title = "Political Text Coding #"+str(i+c)

	# Workers get paid +$0.03 a sentence, and 
	reward = .03 * num_hit_questions

	# Create HITs
	for j in xrange(hits_to_push):
		hit_res = mturk.create_hit(title=hit_title,
					description=hit_description,
					reward=reward,
					duration=duration,
					keywords=keywords,
					# approval_delay=approval_delay,
					question=external_question,
					lifetime=lifetime,
					max_assignments=assignments,
					qualifications=qual)
		hit_results.extend(hit_res)

	## Output to stdout
	print "#################################"
	print str(len(hit_results))+" HIT(s) POSTED!"
	print "#################################"

