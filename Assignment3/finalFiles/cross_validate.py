#!/usr/bin/python

import sys
import os
import fileinput
import re
import random

# expects number of folds and the training file as the 2 inputs
# also expects eval.py to be in the same directory
#
# divides the data into training, testing for each fold and invokes Bubernak_Phadke_IOBTagger.py to run it

folds = int(sys.argv[1])

sentences = []
sentence = []

with open(sys.argv[2],'r') as fd:
	for line in fd:
		line = line.strip()
		if line == "":
			if sentence:
				sentence.append('\n')
				sentences.append(sentence)
				sentence = []
		else:
			sentence.append(line+'\n')

if sentence:
	sentences.append(sentence)

random.seed(100) #initialize so we get the same set of files every time
random.shuffle(sentences)

with open('cv-key.txt', 'w') as fd_gold: 

	try:
    		os.remove('cv-sys-out.txt')
	except OSError:
    		pass

	for i in range(folds):

		print 'performing fold ',i
		fd_train = open('_train.txt', 'w')
		fd_test = open('_test.txt', 'w')
		
		for s in range(len(sentences)):
			if i==s%folds:
				for line in sentences[s]:
					if line=='\n':
						fd_test.write('\n')
					else:
						fd_test.write(line.strip().split()[0]+'\n')
					fd_gold.write(line)
			else:
				for line in sentences[s]:
					fd_train.write(line)

		fd_train.close()
		fd_test.close()

		# make sure to change thus to the way you invoke your code
		os.system('python ./Bubernak_Phadke_IOBTagger.py _train.txt _test.txt _out-part.txt')
		
		os.system('cat _out-part.txt >> cv-sys-out.txt')

os.remove('_test.txt')
os.remove('_train.txt')
os.remove('_out-part.txt')


# the script will leave 'cv-key.txt' and 'cv-sys-out.txt' in the current directory
os.system('python eval.py cv-key.txt cv-sys-out.txt') 
