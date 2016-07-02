from collections import defaultdict
import numpy


def get_gold():
	file_in = open('ratings.txt','r')
	file_out1 = open('adult_index.txt','w')
	file_out2 = open('adult_gold_common_workers.txt','w')

	n = 0
	item_to_index = {}
	num_answers = {}
	answers = {}
	workers_answering = defaultdict(list)

	m = 0
	worker_to_index = {}

	num_items = 0
	num_workers = 0

	for line in file_in:
		splits = line.split()

		item = splits[1]
		worker = splits[0]
		label = splits[2]

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

		if label == "G":
			answers[i,j] = 0
		elif label == "P":
			answers[i,j] = 1
		else:
			answers[i,j] = 2
		workers_answering[i].append(j)

	print n, m, num_items, num_workers

	gold = {}
	for i in range(n):
		list_answers = []
		for j in workers_answering[i]:
			list_answers.append(answers[i,j])
		gold[i] = int(numpy.median(numpy.array(list_answers)))
	print "Gold truth = ", gold

	file_out1.write(str(item_to_index)+'\n')
	file_out1.write(str(worker_to_index)+'\n')

	common_worker_set = set(workers_answering[0])
	for i in range(n):
		common_worker_set = common_worker_set & set(workers_answering[i])
	print "Common worker set = ", len(common_worker_set), common_worker_set
	common_worker_set = list(common_worker_set)

	for i in range(n):
		for j in common_worker_set:
			file_out2.write(str(i)+'\t')
			file_out2.write(str(common_worker_set.index(j))+'\t')
			file_out2.write(str(gold[i])+'\t')
			file_out2.write(str(answers[i,j])+'\n')


get_gold()
