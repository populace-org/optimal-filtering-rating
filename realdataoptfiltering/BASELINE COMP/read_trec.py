from collections import defaultdict
in_file = "trec_hcb_data.txt"


def load():
    with open(in_file, "r") as fp:
        num_responses = defaultdict(int)
        for i, line in enumerate(fp):
            if i == 0:
                continue
            parts = line.split('\t')
            worker = parts[2]
            item = parts[3]
            num_responses[item] += 1

    print len(num_responses)
    print num_responses[max(num_responses, key=num_responses.get)]

load()
