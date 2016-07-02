import math
from collections import defaultdict
#import matplotlib.pyplot as matplotlib.pyplot
from matplotlib.pyplot import *
import copy
import time
import random
import operator
from matplotlib.backends.backend_pdf import PdfPages
import sys

def retain_gold():
	file_in = open('trec-rf10-crowd/trec-rf10-data.txt','r')
	file_out = open('trec-rf10-crowd/trec-cleaned.txt','w')
	for i, line in enumerate(file_in):
		if i == 0:
			continue
		gold = int(line.split('\t')[3])
		label = int(line.split('\t')[4])
		# print gold
		if gold in [0,1,2] and label in [0,1,2]:
			file_out.write(line)

def relabel_n_m():
	file_in = open('trec-rf10-crowd/trec-cleaned.txt','r')
	file_out = open('trec-rf10-crowd/trec-cleaned-indexed.txt','w')

	n = 0
	item_to_index = {}
	num_answers = {}

	m = 0
	worker_to_index = {}

	num_items = 0
	num_workers = 0

	for line in file_in:
		splits = line.split('\t')

		item = splits[0] + splits[2]
		worker = splits[1]
		gold = splits[3]
		label = splits[4]

		if item in item_to_index:
			i = item_to_index[item]
			num_answers[i] += 1
		else:
			i = n
			n += 1
			num_items += 1
			item_to_index[item] = i
			num_answers[i] = 1

		if worker in worker_to_index:
			j = worker_to_index[worker]
		else:
			j = m
			m += 1
			num_workers += 1
			worker_to_index[worker] = j

		write_line = \
			str(i) + '\t' + \
			str(j) + '\t' + \
			gold + '\t' + \
			label

		file_out.write(write_line)
	
	file_out.close()
	file_in.close()
	item_to_index.clear()
	worker_to_index.clear()

	# print "#items = ", num_items, ", #workers = ", num_workers

	# print "(Item, #answers) -- "
	sorted_i = sorted(num_answers.items(), key=operator.itemgetter(1))
	num_items_with_num_answers = defaultdict(int)
	for (key, val) in sorted_i:
		# print key, val
		num_items_with_num_answers[val] += 1

	# print "Num items with num answers -- "
	# print num_items_with_num_answers

	dataset_with_min_answers_per(num_answers)

def dataset_with_min_answers_per(num_answers):
	min_answers = 6
	# file_out = open('trec-rf10-crowd/trec-'+str(min_answers)+'.txt','w')
	file_out = open('temp_test.txt','w+')
	file_in = open('trec-rf10-crowd/trec-cleaned-indexed.txt','r')

	n = 0
	item_to_index = {}
	num_answers_new = {}

	m = 0
	worker_to_index = {}

	num_items = 0
	num_workers = 0

	for line_no, line in enumerate(file_in):
		splits = line.split('\t')

		if line == '':
			continue

		# print line_no, line

		item = splits[0]
		worker = splits[1]
		gold = splits[2]
		label = splits[3]

		if num_answers[int(item)] < min_answers:
			continue

		if item in item_to_index:
			i = item_to_index[item]
			num_answers_new[i] += 1
		else:
			i = n
			n += 1
			num_items += 1
			item_to_index[item] = i
			num_answers_new[i] = 1

		if worker in worker_to_index:
			j = worker_to_index[worker]
		else:
			j = m
			m += 1
			num_workers += 1
			worker_to_index[worker] = j

		write_line = \
			str(i) + '\t' + \
			str(j) + '\t' + \
			gold + '\t' + \
			label

		file_out.write(write_line)

	print "#items = ", num_items, ", #workers = ", num_workers
	print num_answers_new

# retain_gold()
dataset_with_min_answers_per(6)
# relabel_n_m()