#Assignment2
#Matt Bubernak
from __future__ import division
import re
import collections
import math
import cPickle as pickle
import sys

import re

# Defines a tag object
class TagObject:
	def __init__(self, tag):
		self.tag = tag
		self.wordCounts = collections.OrderedDict()
		self.tagCounts = collections.OrderedDict()
		self.featureCounts = collections.OrderedDict()
		self.totalTagOccurances = 0

	def probabilityWord(self,word):
		if word in self.wordCounts:
			return float(self.wordCounts[word] / self.totalTagOccurances)
		else:
			return float(.05 / self.totalTagOccurances)	

	def probTagGivenThis(self,tag):
		if tag in self.tagCounts:
			return float(self.tagCounts[tag] / self.totalTagOccurances)
		else:
			return float(.15 / self.totalTagOccurances)

	def addWord(self,word):
		self.totalTagOccurances += 1

		if word in self.wordCounts:
			self.wordCounts[word] += 1
		else:
			self.wordCounts[word] = 1

	def probFeature(self,feature):
		if (feature[-1:] == "Y"):
			return float(self.featureCounts[feature] / self.featureCounts[feature] + self.featureCounts[feature[0:-1] + "N"])
		else:
			return float(self.featureCounts[feature] / self.featureCounts[feature] + self.featureCounts[feature[0:-1] + "Y"])
	def addFeature(self,feature):
		if feature in self.featureCounts:
			self.featureCounts[feature] += 1
		else:
			self.featureCounts[feature] = 1		
	
	def addTag(self,tag):
		if tag in self.tagCounts:
			self.tagCounts[tag] += 1
		else:
			self.tagCounts[tag] = 1

	def smooth(self):
		#print "smooth"
		for word in self.wordCounts:
			self.wordCounts[word] +=1
			self.totalTagOccurances+=1
		for tag in self.tagCounts:
			self.tagCounts[tag] += 1

# Takes a filename, word array, and tag array, and reads reads them all into array, also populates a worddict with counts of each #
# This replaces all periods with END, and starts each sentence with START. 
def readFileToArrays(fileName,words,tags,wordDict,tagDict):
	file = open(fileName)
	lines = file.readlines()
	
	# Initliaze the array with a START
	words.append("START")
	tags.append("START")

	for line in lines:
		# Skip Newline
		if (line != "\n" ):
			part1 = re.split("\t",line)			
			part2 = re.split("\n",part1[1])
			words.append(part1[0])
			tags.append(part2[0])
		else:
			words.append("END")
			words.append("START")
			tags.append("END")
			tags.append("START")

	# Append an END to the end.
	if tags[len(tags)-1] == "START":
		tags[len(tags)-1] = "END" 
	if words[len(words)-1] == "START":
		words[len(words)-1] = "END" 

	#wordDict now has counts of each word, and the number of occurances 
	for word in words:
		if word in wordDict:
			wordDict[word] = wordDict[word] +1
		else:
			wordDict[word] = 1
			
	#tagDict now has counts for each tag
	for tag in tags:
		if tag in tagDict: 
			tagDict[tag] = tagDict[tag] + 1
		else: 
			tagDict[tag] = 1


def getDerivations(word):
	#is it all capital? 
	#Is it first capital? 
	#Suffix 
	#Prefix
	#lemmaize: remove common suffixes. 
	#POS tagger?? Probabably would be useful. 
	#medical dictionary?

	derivations = []

	#Multiple Capital Letters

	#Suffix IN
	if (len(word) > 2):
		if (word[-2:] == "in"):
			derivations.append("Suffix_IN_Y")
		else:
			derivations.append("Suffix_IN_N")
	#Suffix ASE
	if (len(word) > 3):
		if (word[-3:] == "ase"):
			derivations.append("Suffix_ASE_Y")
		else:
			derivations.append("Suffix_ASE_N")

	return derivations

# Populates tag objects with the necessary probabilities 
def createCounts(tagObjects,words,tags):
	for i in range(0,len(words)-1):
		tagObjects[tags[i]].addWord(words[i])

		# Temporarily add some other derivational words. 
		## COMMENT OUT TO REMOVE ANY CHANGSE FROM ORIGINAL STRAT ##
		#derivations = getDerivations(words[i])
		#for derivation in derivations:
			#tagObjects[tags[i]].addFeature(derivation)
		############################################################
		tagObjects[tags[i]].addTag(tags[i+1])

	for i in range(0,len(tagObjects)):
		tagObjects[tagObjects.keys()[i]].smooth()


def viterbi(observations, tagObjects,tags,predictedStates):
	
	########################SETUP#########################

	N = len(tagObjects) # Number of States
	T = len(observations) # Number of Observations

	# Initialize our Viterbi Matrix 
	viterbi = [[0 for x in range(N+2)] for x in range(T)] 
	# Initilize our Backpointer Matrix
	backpointer = [[0 for x in range(N+2)] for x in range(T)]  

	####################INITIALIZATION####################

	# Set the initial probability for each tag. 
	for s in range(0,N): 
		# Probability of tag given "START" state before it. 
		probTagGivenStart = -math.log(tagObjects["START"].probTagGivenThis(tagObjects.keys()[s]))
		# Probability of the word given the tag. 
		probWordGivenTag = -math.log(tagObjects[tagObjects.keys()[s]].probabilityWord(observations[0])) 
		# Set the first viterbi probability
		viterbi[0][s] = probTagGivenStart+probWordGivenTag
		# Initialize the first backpointer to START
		backpointer[0][s] = "START" 

	######################RECURSION#######################
	# For each observation(word) 
	for t in range(1,T):

		# For each state(tag)
		for s in range(0,N):

			#Viterbi Value Calculation
			minVal1 = 99999999999999
			viterbi[t][s] = 0
			# For each previous tag 
			for x in range(0,N):
				# Previous Viterbi Value
				prevVit = viterbi[t-1][x]
				# Probability of this state(tag) given the previous state(tag) 
				probTagGivenPrev = -math.log(tagObjects[tagObjects.keys()[x]].probTagGivenThis(tagObjects[tagObjects.keys()[s]].tag))
				
				# Probability of this observation(word) given the state(tag)
				probWordGivenTag = -math.log(tagObjects[tagObjects.keys()[s]].probabilityWord(observations[t])) #*5

				# Check if any derivations of this word have a better probability
				####COMMENT OUT TO REMOVE ANY CHANGSE FROM ORIGINAL STRATS ####
				derivations = getDerivations(observations[t])
				
				#for derivation in derivations:
					#tagObjects[tagObjects.keys()[s]].probFeature(derivation)

					#if (derivation == "ase_GEN_" and tagObjects.keys()[s] == "B"):
						#print "found it! " + observations[t] 
						#probabilityTag = 0
					#if -math.log(tagObjects[tagObjects.keys()[s]].probabilityWord(derivation)) < probWordGivenTag:
					#	probWordGivenTag = -math.log(tagObjects[tagObjects.keys()[s]].probabilityWord(derivation))
					#probWordGivenTag += -math.log(tagObjects[tagObjects.keys()[s]].probabilityWord(derivation))
				#probWordGivenTag = probWordGivenTag / (len(derivations) + 1)
				########3


				# If we have a new max, update the viterbi value
				if (prevVit + probTagGivenPrev + probWordGivenTag < minVal1):
					minVal1 = prevVit + probTagGivenPrev + probWordGivenTag
					viterbi[t][s] = minVal1
					#backpointer[t][s] = tagObjects[tagObjects.keys()[x]].tag


			#Backpointer Value Calcuation			
			minVal2 = 99999999999999
			backpointer[t][s] = "NULL"
			# For each previous tag 
			for x in range(0,N):
				# Previous Viterbi Value
				prevVit = viterbi[t-1][x]
				# Probability of this state(tag) given the previous state(tag) 
				probTagGivenPrev = -math.log(tagObjects[tagObjects.keys()[x]].probTagGivenThis(tagObjects[tagObjects.keys()[s]].tag))
				
				# If we have a new max, update the backpointer
				if (prevVit + probTagGivenPrev < minVal2):
					minVal2 = prevVit + probTagGivenPrev
					backpointer[t][s] = tagObjects[tagObjects.keys()[x]].tag			

	####################TERMINATION####################
	# Determine the best score
	bestScore = 0
	startOfBacktrace = 0
	minVal = 99999999999999
	# For each state(tag) 
	for s in range(0,N):
		# Grab the last viterbi val
		viterbiVal = viterbi[T-1][s]
		# Check if this is the maximum final viterbi value, aka the start point for our backtrace. 
		if (viterbiVal < minVal):
			minVal = viterbiVal + probTagGivenPrev
			bestScore = minVal
			startOfBacktrace = tagObjects[tagObjects.keys()[s]].tag

	######################RETURN######################
	# Instead of returning, this is where we update our array of predicated states 
	# For each word(ignore the first "START")
	for t in range (1,T):
		minVal = 999999999999
		bestTag = "NULL"
		# For each tag, determine the best. 
		for s in range (0,N):
			# If we have a new max, grab the value and the backpointer value
			if (viterbi[t][s] < minVal):
				minVal = viterbi[t][s]
				bestTag = backpointer[t][s]

		# Append the tag we selected to our predictedStates array. 
		predictedStates.append(str(bestTag))
	return 



# Takes a filename, word array, and tag array, and reads reads them all into array, also populates a worddict with counts of each #
def readFileToSentences(fileName,sentences):
	i = 0
	file = open(fileName)
	lines = file.readlines()
	# Append a new blank array
	sentences.append([])
	# Append a start for the first sentence
	sentences[0].append("START")
	# For each line
	for line in lines:
		# If we hit a newline, skip it. 
		if (line  != '\n'):
			# Grab the first part
			part1 = re.split('\s',line)
			sentences[i].append(part1[0])
			#print "adding: " + part1[0] + " to sentence: " + str(i)

		#skip blank lines
		else:
			sentences[i].append("END")
			i +=1
			sentences.append([])
			sentences[i].append("START")
			
	sentences[i].append("END")

	# We add one too many sentences, so pop the last one
	#sentences.pop()



#main function
def main():
	trainingDataFileName = sys.argv[1]
	testingDataFileName = sys.argv[2]
	outputDataFilename = sys.argv[3]
	# Create empty array of words/tags for training data
	words = []
	tags = []
	wordDict = collections.OrderedDict() 
	tagDict = collections.OrderedDict()

	# Read all the words from the training file into the arrays 
	readFileToArrays(trainingDataFileName,words,tags,wordDict,tagDict)
	
	# Create all our tag objects
	tagObjects = collections.OrderedDict()
	for tag in tagDict:
		tagObjects[tag] = TagObject(tag)

	# Populate word/tag counts for each bigram
	createCounts(tagObjects,words,tags)

	# Empty arrays for the sentences and sentence tags
	sentences = []
	sentenceTags = []	
	# Populate the sentences array 
	readFileToSentences(testingDataFileName,sentences)

	# Open the output file 
	f1=open(outputDataFilename,'w+')
	count = 0
	# For each sentence
	for sentence in sentences:

		# Use viterbi to generate tags for the sentence
		sentenceTags = []
		viterbi(sentence,tagObjects,tags,sentenceTags)

		# For i sentences
		for i in range(0,len(sentence)-1):
			# Ignore the START
			if (sentence[i] != "START"):
				# Print the sentence with it's tag. 
				f1.write(sentence[i] + "\t" + sentenceTags[i] + "\n")
				#f1.write("\n") #temp
		#f1.write("\n") #temp
		#f1.write(".\t.")
		count+=1
		# Append new lines if this is not the last sentene. 
		if (count != len(sentences)):
			f1.write("\n")

	# Close the file when we are done. 
	f1.close()

main()

