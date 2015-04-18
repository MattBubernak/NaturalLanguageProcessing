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
tagTotalCounts = {0:0, 1:0, 2:0}
emission_cnt = [{} for _ in xrange(len(tagList))]
transition_cnt = [[0 for _ in xrange(len(tagList))] for _ in xrange(len(tagList))]

emission_allCapital_cnt = [[0,0] for _ in xrange(len(tagList))]
emission_firstCapital_cnt = [[0,0] for _ in xrange(len(tagList))]
emission_feature3_cnt = [[0,0] for _ in xrange(len(tagList))]
emission_feature4_cnt = [[0,0] for _ in xrange(len(tagList))]
emission_feature5_cnt = [[0,0] for _ in xrange(len(tagList))]
firstTag_cnt = [0 for _ in xrange(len(tagList))]

emission_prob = [{} for _ in xrange(len(tagList))]
emission_allCapital_prob = [[0,0] for _ in xrange(len(tagList))]
emission_firstCapital_prob = [[0,0] for _ in xrange(len(tagList))]
emission_feature3_prob = [[0,0] for _ in xrange(len(tagList))]
emission_feature4_prob = [[0,0] for _ in xrange(len(tagList))]
emission_feature5_prob = [[0,0] for _ in xrange(len(tagList))]

transition_prob = [None for _ in xrange(len(tagList))]
firstTag_prob = [None for _ in xrange(len(tagList))]

# weight for [emission_prob, emission_firstCaptial_prob, emission_allCapital_prob]
weights = [0.9999995, 0.0000000005, 0.0000004700,0.000000028,0.00000000075 ,0.00000000075 ]
#weights = [0.9999995, 0.000000000, 0.00000000,0.000000000,0.00000005]

isAllCapitalRE = r"^[A-Z]+$"
isFirstCapitalRE = r"[A-Z]+"
isNumberAndCapRE = r"^(?=.*\d)(?=.*[A-Z])[A-Z\d]"
isInSuffix = r"^.+in$"
isAseSuffix = r"^.+ase$"

def extractFeature(word):

	"""
	Given one word, return the matching of the feature
	1 for True, 0 for False
	word = "AAb" -> return [0, 1]
	word = "AAB" -> return [0, 0]
	word = "bbA" -> return [0, 0]
	"""

	#if (re.match(isInSuffix,"meenin")):
	#	print "match"
	#else:
	#	print "not match"

	return [1 if (t != None) else 0 for t in [re.match(isAllCapitalRE, word), re.match(isFirstCapitalRE, word), re.match(isNumberAndCapRE, word),re.match(isInSuffix, word),re.match(isAseSuffix, word)]]

def viterbiPath(tokenList):
	"""
	Given the a list of token(word), go through the viterbi algorithm
	"""
	viterbiTable = [ [ 0.0 for _ in xrange(len(tagList)) ] for _ in xrange(len(tokenList)) ]
	backPointer = [ [ -1 for _ in xrange(len(tagList)) ] for _ in xrange(len(tokenList)) ]

	tinyProb = math.exp(-100)
	startOfBacktrace = 0
	if len(tokenList) == 0:
		return []
	for (wordIdx, word) in enumerate(tokenList):
		(isAllCapital, isFirstCapital, feature3,feature4,feaure5) = extractFeature(word)
		for tagID in xrange(len(tagList)):
			if wordIdx == 0:
				# first word: just use the emission prob
				#viterbiTable[wordIdx][tagID] = (tinyProb if firstTag_prob[tagID] == None else firstTag_prob[tagID]) * (tinyProb if word not in emission_prob[tagID] else emission_prob[tagID][word]

				if firstTag_prob[tagID] == None:
					viterbiTable[wordIdx][tagID] = tinyProb
				else:
					viterbiTable[wordIdx][tagID] = firstTag_prob[tagID]
				if word not in emission_prob[tagID]:
					viterbiTable[wordIdx][tagID] *= tinyProb
				else:
					viterbiTable[wordIdx][tagID] *= emission_prob[tagID][word]
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
				tProb += weights[1] * (tinyProb if emission_allCapital_prob[tagID][isAllCapital] == 0 else emission_allCapital_prob[tagID][isAllCapital])
				tProb += weights[2] * (tinyProb if emission_firstCapital_prob[tagID][isFirstCapital] == 0 else emission_firstCapital_prob[tagID][isFirstCapital])
				tProb += weights[3] * (tinyProb if emission_feature3_prob[tagID][feature3] == 0 else emission_feature3_prob[tagID][feature3])
				tProb += weights[4] * (tinyProb if emission_feature4_prob[tagID][feature4] == 0 else emission_feature4_prob[tagID][feature4])
				tProb += weights[5] * (tinyProb if emission_feature5_prob[tagID][feature5] == 0 else emission_feature5_prob[tagID][feature5])
				# and calculate other feature
				maxProb =  maxProb * tProb
				viterbiTable[wordIdx][tagID] = maxProb
				#print "Just updated table for word: " + tokenList[wordIdx] + " and tag: " + tagList[tagID] + " to be: " + str(maxProb)
				#print str(emission_prob[1][1])
	#Trace back to find out the best labeling path by using backPointer
	# return the label for each token
	labelSent = []

	startOfBackTrace = 0
	maxVal = 0
	for tag in range(0,3):
		#print " tag: " + tagList[tag] +" "+ str(viterbiTable[len(testSent)-1][tag])
		#print "tag:" + str(tag)
		viterbiVal = viterbiTable[len(tokenList)-1][tag]
		# Check if this is the maximum final viterbi value, aka the start point for our backtrace. 
		if (viterbiVal > maxVal):
			maxVal = viterbiVal
			startOfBacktrace = tag

	#print str(startOfBacktrace)
	#print "starting our backtrace at: " + tagList[startOfBacktrace]
	
	cur = startOfBacktrace
	#print "cur: " + str(cur)
	#print "appending: " + tagList[cur]
	labelSent.insert(0,tagList[cur])
	for (wordIdx, word) in enumerate(tokenList):
		if len(tokenList)-1-wordIdx == 0:
			break
		else: 
			cur = backPointer[len(tokenList)-1-wordIdx][cur]
			#print "appending: " + tagList[cur]
			labelSent.insert(0,tagList[cur])

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

		# Initialize prevTagID to be -1 to start. 
		prevTagID = -1

		# Counting
		# Read each line. 
		for line in fhd.xreadlines():
			# Strip any newlines from the end
			line = line.strip()
			# If we have a blank line, reset the prevTag
			if line == "":
				prevTagID = -1

			else:
				# Grab the word/tag
				(word, tag) = line.split("\t")

				# Extract all the possible features of the word. 
				(isAllCapital, isFirstCapital,feature3,feature4,feature5) = extractFeature(word)
				# Get the tag
				tagID = tagType[tag]

				tagTotalCounts[tagID] += 1

				# If this is the start of the sentence
				if prevTagID == -1:
					# Add to the firstTag cnt for this tag. 
					firstTag_cnt[tagID] += 1
				else:
					# Otherwise update our ransition count matrix 
					transition_cnt[prevTagID][tagID] += 1
				# Save this tag as the previous tag. 
				prevTagID = tagID

				# deal with the emission_cnt, emission_allCapital_cnt, emission_firstCapital_cnt, and other emission feature count by yourself
				if word not in emission_cnt[tagID]:
					emission_cnt[tagID][word] = 0

				emission_cnt[tagID][word] += 1 
				emission_allCapital_cnt[tagID][isAllCapital] += 1
				emission_firstCapital_cnt[tagID][isFirstCapital] += 1
				emission_feature3_cnt[tagID][feature3] += 1
				emission_feature4_cnt[tagID][feature4] += 1
				emission_feature5_cnt[tagID][feature5] += 1




	# calculate the prob
	total_firstTag = sum(firstTag_cnt)
	# For each possible tag
	for tagID in xrange(len(tagList)):

		# Calculate all of our transition probabilities. 
		total_prevTag = sum( [transition_cnt[tagID][currentTagID] for currentTagID in xrange(len(tagList))] )
		transition_prob[tagID] = [ None if transition_cnt[tagID][currentTagID] == 0 else transition_cnt[tagID][currentTagID]/float(total_prevTag) for currentTagID in xrange(len(tagList)) ]
		
		# Calculate all of our emission probabilities. 
		for word in emission_cnt[tagID]:
			emission_prob[tagID][word] = emission_cnt[tagID][word]/float(tagTotalCounts[tagID])
		#print tagTotalCounts[tagID]
		#emission_prob[tagID] = [ None if emission_cnt[tagID][word] == 0 else emission_cnt[tagID][word]/float(tagTotalCounts[tagID]) for word in emission_cnt[tagID] ]

		#print tagID
		emission_allCapital_prob[tagID] = [ 0 if emission_allCapital_cnt[tagID][num] == 0 else emission_allCapital_cnt[tagID][num]/float(emission_allCapital_cnt[tagID][0] + emission_allCapital_cnt[tagID][1]) for num in range(2) ]
		emission_firstCapital_prob[tagID] = [ 0 if emission_firstCapital_cnt[tagID][num] == 0 else emission_firstCapital_cnt[tagID][num]/float(emission_firstCapital_cnt[tagID][0] + emission_firstCapital_cnt[tagID][1]) for num in range(2) ]
		emission_feature3_prob[tagID] = [ 0 if emission_feature3_cnt[tagID][num] == 0 else emission_feature3_cnt[tagID][num]/float(emission_feature3_cnt[tagID][0] + emission_feature3_cnt[tagID][1]) for num in range(2) ]
		emission_feature4_prob[tagID] = [ 0 if emission_feature4_cnt[tagID][num] == 0 else emission_feature4_cnt[tagID][num]/float(emission_feature4_cnt[tagID][0] + emission_feature4_cnt[tagID][1]) for num in range(2) ]
		emission_feature5_prob[tagID] = [ 0 if emission_feature5_cnt[tagID][num] == 0 else emission_feature5_cnt[tagID][num]/float(emission_feature5_cnt[tagID][0] + emission_feature5_cnt[tagID][1]) for num in range(2) ]

	# Read Test, write the label to labelFile
	testSent = []
	with open(devFile, "r") as fhd, open(labelFile, "w") as fhd_write:
		# For every line of the test file
		for line in fhd.xreadlines():
			# Read the line
			line = line.strip()
			# If it's a blank line
			if line == "":
				# Send the current sentence to the viterbi algorithm. 
				labelSent = viterbiPath(testSent)

				# write label file
				for i in range(0,len(testSent)):
					fhd_write.write(testSent[i] + "\t" + labelSent[i] + "\n")
				fhd_write.write("\n")
				# Empty the test set. 
				testSent = []
			# If it's not a blank line
			else:
				#print line
				# Read each line
				if "\t" in line:
					(word, label) = line.split("\t")
				else:
					word = line
				# Append the current word to the testSent
				testSent.append(word)
		#deal with the last sentence
		labelSent = viterbiPath(testSent)
		# write  label file
		for i in range(0,len(testSent)):
			fhd_write.write(testSent[i] + "\t" + labelSent[i] + "\n")
