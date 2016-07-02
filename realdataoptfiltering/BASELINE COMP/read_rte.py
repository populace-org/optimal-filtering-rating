from collections import defaultdict
in_file = "temp.standardized.tsv"
# in_file = "rte.standardized.tsv"


def load():
    with open(in_file, "r") as fp:
        num_responses = defaultdict(int)
        for i, line in enumerate(fp):
            if i == 0:
                continue
            parts = line.split('\t')
            worker = parts[1]
            item = parts[2]
            num_responses[item] += 1

    print num_responses
    print len(num_responses)
    print num_responses[min(num_responses, key=num_responses.get)]

load()
