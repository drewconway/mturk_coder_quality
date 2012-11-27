#!/usr/bin/env python
# encoding: utf-8
"""
generate_hit.py.py

Description:	Creates a HIT for experiments of coder quality.  Hit contains a Qualification 
				test and an external questions hosted on S3.

Created by  (drew.conway@nyu.edu) on
# Copyright (c) , under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, Requirement
from boto.mturk.question import ExternalQuestion
# from boto.mturk.question import Overview,AnswerSpecification,SelectionAnswer,FormattedContent
# from scipy import random
# import json

from generate_qualification import CoderQualityQualificationTest,CoderQualityQualificationType

def open_mturk_connection(acct):
	return MTurkConnection(aws_access_key_id = acct["access_key"], 
						   aws_secret_access_key = acct["secret_key"], 
						   host = acct["host"])

if __name__ == '__main__':

	from datetime import datetime

	# Account data
	acct = {"access_key" : "AKIAIHR7KNG5J645RGEQ", 
	"secret_key" : "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", 
	"host" : "mechanicalturk.sandbox.amazonaws.com"}

	## Create qualification type

	# Qualification test info
	n = 4
	c = 3
	data_dir = "../../data/"
	title = "Qualification test for recording the contents of political text on economic and social scales"
	
	# Create qualification test object
	qual_test = CoderQualityQualificationTest(n, c, data_dir+"test_with_answers.json", title)

	# Qualification Type info
	qual_name = "Test Questions With Known Answers ID: "+datetime.now().strftime("%s")
	qual_description = "A qualification test in which you read sentences from political texts and judge whether these deal with economic or social policy."
	keywords = ["text","coding","political"]
	duration = 30*60

	# Open MTurk connection
	mturk = open_mturk_connection(acct)

	# Create new qualification type
	qual_type = CoderQualityQualificationType(mturk, qual_test, qual_name, qual_description, keywords, duration, create=True)

	## Register test as a requirement for hit
	qual_id = "2WQBAT2D5NQYWC2YYWAG8TYMNFX732"
	qual_id = qual_type.get_type_id()
	req = Requirement(qualification_type_id=qual_id, 
					  comparator="GreaterThan", 
					  integer_value=0)
	qual = Qualifications()
	qual.add(req)

	### Create HIT with qualification test

	# Question data
	hit_title = "HIT Test ID: "+datetime.now().strftime("%s")
	num_hit_questions = 4
	external_url = "https://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/index.html?n="+str(num_hit_questions)
	hit_description = "This task involves reading sentences from political texts and judging whether these deal with economic or social policy."

	# Setup
	reward = 0.11
	assignments = 5
	duration = 3600
	lifetime = 259200
	approval_delay = 1296000

	# Create Question for HIT
	external_question = ExternalQuestion(external_url=external_url, frame_height=800)

	# Create HITs with qualification test
	hits_to_push = 1
	hit_results = []
	for i in xrange(hits_to_push):
		hit_res = mturk.create_hit(title=hit_title,
					description=hit_description,
					reward=reward,
					duration=duration,
					keywords=keywords,
					approval_delay=approval_delay,
					question=external_question,
					lifetime=lifetime,
					max_assignments=assignments,
					qualifications=qual)
		hit_results.append(hit_res[0])
