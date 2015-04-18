#!/usr/bin/env python
import math
import os, sys
import re

#emissin_prob: P( word | tag )
#transition_rrob: P( tag_i | tag_{i-1} )
#emission_firstCapital_prob: P( the character is capitalized (0 or 1) | tag )
#emission_allCapital_prob: P( all character are capitalized (0 or 1) | tag )
tagList = ["I", "B", "O"]
tagType = {"I":0, "B":1, "O":2}
emission_cnt = [{} for _ in xrange(len(tagList))]
transition_cnt = [[0 for _ in xrange(len(tagList))] for _ in xrange(len(tagList))]

emission_allCapital_cnt = [[0,0] for _ in xrange(len(tagList))]
emission_firstCapital_cnt = [[0,0] for _ in xrange(len(tagList))]
firstTag_cnt = [0 for _ in xrange(len(tagList))]

emission_prob = [None for _ in xrange(len(tagList))]
emission_allCapital_prob = [[0,0] for _ in xrange(len(tagList))]
emission_firstCapital_prob = [[0,0] for _ in xrange(len(tagList))]

transition_prob = [None for _ in xrange(len(tagList))]
firstTag_prob = [None for _ in xrange(len(tagList))]

# weight for [emission_prob, emission_firstCaptial_prob, emission_allCapital_prob]
weights = [0.9999995, 0.00000005, 0.00000045]

isAllCapitalRE = r"^[A-Z]+$"
isFirstCapitalRE = r"^[A-Z]"

def extractFeature(word):

	"""
	Given one word, return the matching of the feature
	1 for True, 0 for False
	word = "AAb" -> return [0, 1]
	word = "AAB" -> return [0, 0]
	word = "bbA" -> return [0, 0]
	"""
	return [1 if (t != None) else 0 for t in [re.match(isAllCapitalRE, word), re.match(isFirstCapitalRE, word), re.match(RE, word), re.match()]]

def viterbiPath(tokenList):
	"""
	Given the a list of token(word), go through the viterbi algorithm
	"""
	viterbiTable = [ [ 0.0 for _ in xrange(len(tagList)) ] for _ in xrange(len(tokenList)) ]
	backPointer = [ [ -1 for _ in xrange(len(tagList)) ] for _ in xrange(len(tokenList)) ]

	tinyProb = math.exp(-100)

	for (wordIdx, word) in enumerate(tokenList):
		(isAllCapital, isFirstCapital) = extractFeature(word)
		for tagID in xrange(len(tagList)):
			if wordIdx == 0:
				# first word: just use the emission prob
				viterbiTable[wordIdx][tagID] = (tinyProb if firstTag_prob[tagID] == None else firstTag_prob[tagID]) * (tinyProb if word not in emission_prob[tagID] else emission_prob[tagID][word])
			else:
				# following word: use both emission prob (mixture) and transition prob
				maxProb = 0.0

				# transition prob
				for prevTagID in xrange(len(tagList)):
					tProb = (tinyProb if transition_prob[prevTagID][tagID] == None else transition_prob[prevTagID][tagID]) * viterbiTable[wordIdx-1][prevTagID]
					if tProb > maxProb:
						maxProb = tProb 
						backPointer[wordIdx][tagID] = prevTagID
				# omission prob
				tProb = weights[0] *  (tinyProb if word not in emission_prob[tagID] else emission_prob[tagID][word])
				tProb += weights[1] * emission_allCapital_prob[tagID][isAllCapital]
				tProb += weights[2] * emission_isFirstCapital_prob[tagID][isFirstCapital]
				# and calculate other feature

				maxProb =  maxProb * tProb
				viterbiTable[wordIdx][tagID] = maxProb
	
	#Trace back to find out the best labeling path by using backPointer
	# return the label for each token
	return labelSent
		
if __name__ == "__main__":
	#Check the input parameter is correct
	if len(sys.argv) != 4:
		raise Exception("Please follow this input format: python pa3_tutorial.py TRAIN_FILE DEV_FILE LABEL_FILE")
	trainFile = sys.argv[1]
	devFile = sys.argv[2]
	labelFile = sys.argv[3]
	if os.path.exists(trainFile) != True:
		raise Exception("Train file %s does not exist" % trainFile)
	if os.path.exists(devFile) != True:
		raise Exception("Dev file %s does not exist" % devFile)

	# Read train file
	with open(trainFile, "r") as fhd:
		prevTagID = -1

		# Counting
		for line in fhd.xreadlines():
			line = line.strip()
			if line == "":
				prevTagID = -1
			else:
				(word, tag) = line.split("\t")
				(isAllCapital, isFirstCapital) = extractFeature(word)
				tagID = tagType[tag]

				if prevTagID == -1:
					firstTag_cnt[tagID] += 1
				else:
					transition_cnt[prevTagID][tagID] += 1

				prevTagID = tagID

				# deal with the emission_cnt, emission_allCapital_cnt, emission_firstCapital_cnt, and other emission feature count by yourself
				if word not in emission_cnt[tagID]:
					emission_cnt[tagID][word] = 0
				emission_allCapital_cnt[tagID][isAllCapital] += 1
				#emission_cnt[_][_] += 1 
				#emission_allCapital_cnt[_][_] += 1
				#emission_firstCapital_cnt[_][_] += 1

	# calculate the prob
	total_firstTag = sum(firstTag_cnt)
	for tagID in xrange(len(tagList)):
		total_prevTag = sum( [transition_cnt[tagID][currentTagID] for currentTagID in xrange(len(tagList))] )
		transition_prob[tagID] = [ None if transition_cnt[tagID][currentTagID] == 0 else transition_cnt[tagID][currentTagID]/float(total_prevTag) for currentTagID in xrange(len(tagList)) ]

		# deal with the emission_prob, emission_allCapital_prob, emission_firstCapital_prob, and other emission feature prob by yourself

	# Read Test, write the label to labelFile
	testSent = []
	with open(devFile, "r") as fhd, open(labelFile, "w") as fhd_write:
		for line in fhd.xreadlines():
			line = line.strip()
			if line == "":
				labelSent = viterbiPath(testSent)

				testSent = []

				# write label file
			else:
				(word, label) = line.split()
				testSent.append(word)
		#deal with the last sentence
		labelSent = viterbiPath(testSent)
		# write  label file
