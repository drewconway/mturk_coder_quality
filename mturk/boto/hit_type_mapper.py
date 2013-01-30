#!/usr/bin/env python
# encoding: utf-8
"""
hit_type_mapper.py

Description: Used to map HITId variable to experiment type using a HIT's title

Created by  (drew.conway@nyu.edu) on
# Copyright (c) , under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

from boto.mturk.connection import MTurkConnection
from datetime import datetime
import argparse
import csv
import re

def hitMapper(hit):
	hit_id = hit.HITId
	split_title = re.split("[()#]", hit.Title)
	exp_id = split_title[-2]
	return {"HITId" : hit_id, "ExpId" : exp_id}


if __name__ == '__main__':

	# File path to downloads
	res_dir = "../results/"

	# Record start time
	start_time = datetime.now().strftime("%s")

	# Need to take single user argument for production or sandbox server
	parser = argparse.ArgumentParser(description='This script downloads coding results and approves works.')
	parser.add_argument("--prod", type=str, choices="yn", default="n",
		help="Should we look for results on the production server? Default is 'n', which is the sandbox.")

	# Options to set AWS credentials
	parser.add_argument("--access", type=str, default="",
		help="Your AWS access key. Will look for boto configuration file if nothing is provided")

	parser.add_argument("--secret", type=str, default="",
		help="Your AWS secret access key. Will look for boto configuration file if nothing is provided")

	# Get arguments from user 
	args = parser.parse_args()
	access = args.access
	secret = args.secret

	# Perform server switch
	if args.prod == "n":
		host = "mechanicalturk.sandbox.amazonaws.com"
		res_dir = res_dir + "sandbox/maps/"
	else:
		host = "mechanicalturk.amazonaws.com"
		res_dir = res_dir + "production/maps/"

	# Open log file
	csv_file = open(res_dir+start_time+"_map.csv", "w")

	# Open DictWriter
	writer = csv.DictWriter(csv_file, fieldnames=["HITId", "ExpId"])

	# Open MTurk connection
	if access != "" and secret != "":
		mturk = MTurkConnection(host = host, aws_access_key_id=access, aws_secret_access_key=secret)
	else:
		mturk = MTurkConnection(host = host)


	# Get all HITs
	hits = mturk.get_all_hits()
	hit_list = map(lambda h: h, hits)

	# Mapped HITIds
	hit_id_map = map(hitMapper, hit_list)

	# Output results
	writer.writeheader()
	for m in hit_id_map:
		writer.writerow(m)



