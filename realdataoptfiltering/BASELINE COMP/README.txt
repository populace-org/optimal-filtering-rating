TREC 2011 Crowdsourcing Track
https://sites.google.com/site/treccrowd2011

Task 2 Consensus: Test Data
Released August 19, 2011 by Matt Lease, ml@ischool.utexas.edu.

These relevance judgments were collected as part of the TREC 2010 Relevance Feedback track. 
Use of this data for computing consensus was first described in the following paper:
    
    Wei Tang and Matthew Lease. Semi-Supervised Consensus Labeling for Crowdsourcing. In ACM SIGIR Workshop on Crowdsourcing for Information Retrieval (CIR), 2011.
    http://www.ischool.utexas.edu/~ml/papers/tang-cir11.pdf (updated version with corrections posted Aug. 22, 2011).

Participating groups should cite this year's Track Overview (once written) 
rather than the paper above as the source for data used in the track.

===============================================================
There are 19,033 total (topic,document) examples (noisily) judged by 762 workers, who produced a total of 89624 binary judgments 
(0 = not relevant, 1 = relevant).  

3275 of the examples have prior "gold" (binary) labels by NIST, but we have only released labels for 2275 of them (for training: 
1000 non-rel, 1275 rel). We have reserved 1000 gold labels for evaluation, while examples without prior gold labels ("-1") will be 
evaluated by consensus between teams.

Worker and document IDs have been anonymized.  Gold NIST labels are in the "TRUTH" column, while worker judgments are in the "LABEL" column.

------------------------
Reference: following R code

> data<- read.table('data.txt', header=T)

> names(data)
[1] "TOPIC" "HIT_ID"      "WORKER_ID"   "DOC_ID"      "TRUTH"       "LABEL"

> uniq_examples<- unique(data[c("TOPIC", "DOC_ID", "TRUTH")])

> nrow(uniq_examples)
[1] 19033

> table(uniq_examples$TRUTH)
   -1     0     1
16758  1000  1275

