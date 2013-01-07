#!/usr/bin/env python
# encoding: utf-8
"""
approver.py

Description: Simple script that looks for submitted results and approves them. Run as a cron
job every hour.

Created by  (drew.conway@nyu.edu) on
# Copyright (c) , under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

from boto.mturk.connection import MTurkConnection
from itertools import chain
from datetime import datetime
import argparse
import csv

def formAns(ans_obj):
	ans_tuple = map(lambda a: (a.qid, a.fields), ans_obj)
	return dict(ans_tuple)

def parseAnswer(form, num_sentences=4):
	# Create a dictionary to hold form responses
	form_keys = map(lambda i: ["area_"+str(i), "scale_"+str(i)], xrange(num_sentences))
	form_keys = list(chain.from_iterable(form_keys))
	form_dict = dict.fromkeys(form_keys, None)

	# Stick form response in a dict
	for a in form.answers:
		form_ans = formAns(a)
		for r in form_ans.keys():
			form_dict[r] = form_ans[r][0]

	# Add high-level info
	form_dict["AssignmentId"] = form.AssignmentId
	form_dict["HITId"] = form.HITId
	form_dict["WorkerId"] = form.WorkerId
	form_dict["SubmitTime"] = form.SubmitTime

	# Form responses where no data is recorded will have a None value
	return form_dict


def reviewAssignment(assigments, mturk=None, auto_approve=True):
	answer_list = list()
	for a in assignments:
		if a.AssignmentStatus == "Submitted":
			aid = a.AssignmentId
			answer_list.append(parseAnswer(a))
			if auto_approve:
				mturk.approve_assignment(aid)
	return answer_list


if __name__ == '__main__':

	# File path to downloads
	res_dir = "../results/"

	# Need to take single user argument for production or sandbox server
	parser = argparse.ArgumentParser(description='This script downloads coding results and approves works.')
	parser.add_argument("--prod", type=str, choices="yn", default="n",
		help="Should we look for results on the production server? Default is 'n', which is the sandbox.")

	# Get arguments from user 
	args = parser.parse_args()

	# Perform server switch
	if args.prod == "n":
		host = "mechanicalturk.sandbox.amazonaws.com"
		res_dir = res_dir + "sandbox/"
	else:
		host = "mechanicalturk.amazonaws.com"
		res_dir = res_dir + "production/"

	# Open MTurk connection
	mturk = MTurkConnection(host = host)

	# Download reviewable HITs
	reviewable_hits = list()
	m = 10
	p = 1
	max_page = False
	while not max_page:
		hit_list = mturk.get_reviewable_hits(page_size=m, page_number=p)
		reviewable_hits.extend(hit_list)
		if(len(hit_list) < m):
			max_page = True
		else:
			p += 1

	# Review assignments
	response_list = list()
	for h in reviewable_hits:
		assignments = mturk.get_assignments(h.HITId)
		if len(assignments) > 0:
			response_list.append(reviewAssignment(assignments, mturk))
	responses = list(chain.from_iterable(response_list))

	# # Output file, name simply based on the time it is created
	if len(responses) > 0:
		f = open(res_dir+datetime.now().strftime("%s")+".csv", "w")
		dw = csv.DictWriter(f, fieldnames=responses[0].keys())
		dw.writeheader()
		for r in responses:
			dw.writerow(r)
		f.close()





