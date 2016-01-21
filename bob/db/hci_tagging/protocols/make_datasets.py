#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 18 Jan 17:24:51 CET 2016

import random
import os
import re

random.seed(1)

subjects = range(1, 31)
subjects.remove(29)

# training set - get the subjects
train = random.sample(subjects, 10)
for t in train:
  subjects.remove(t)

# development set
dev = random.sample(subjects, 9)
for d in dev:
  subjects.remove(d)

# test set: what remains
test = subjects

# get the files
train_files = []
dev_files = []
test_files = []

for dirpath, dirnames, filenames in os.walk('../data/Sessions'):

  for filename in filenames:
    sub = re.search('Part_(.+?)_', filename).group(1)
    
    #basename, ext = os.path.splitext(os.path.join(dirpath, filename))
    basename = os.path.dirname(os.path.join(dirpath, filename))

    # this file goes in the training set
    if int(sub) in train:
      train_files.append(basename)
    
    # this file goes in the dev set
    if int(sub) in dev:
      dev_files.append(basename)
    
    # this file goes in the test set
    if int(sub) in test:
      test_files.append(basename)

print train
print "training set contains {0} files".format(len(train_files))
print dev
print "development set contains {0} files".format(len(dev_files))
print test
print "test set contains {0} files".format(len(test_files))

# print list to files
train_list_file = open("default/train.txt", "w")
for f in train_files:
  train_list_file.write("{0}\n".format(f))
train_list_file.close()

dev_list_file = open("default/dev.txt", "w")
for f in dev_files:
  dev_list_file.write("{0}\n".format(f))
dev_list_file.close()

test_list_file = open("default/test.txt", "w")
for f in test_files:
  test_list_file.write("{0}\n".format(f))
test_list_file.close()
