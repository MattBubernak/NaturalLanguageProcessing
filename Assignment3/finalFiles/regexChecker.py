#!/usr/bin/env python

import os, sys
import re

regex  = r"^[a-z]+$"



if (re.match(regex,"1")):
	print "match"
else:
	print "not match"
if (re.match(regex,"aI222")):
	print "match"
else:
	print "not match"
countI = [0.0,0.0]
countB = [0.0,0.0]
countO = [0.0,0.0]

f1 = open(sys.argv[1])
lines = f1.readlines()

for line in lines:
	line = line.strip()	
	if line == "":
		continue

	(word, tag) = line.split("\t")
	
	if (tag == "I"):
		if (re.match(regex, word)):
			countI[0]+=1
		else:
			countI[1]+=1
	if (tag == "B"):
		if (re.match(regex, word)):
			countB[0]+=1
		else:
			countB[1]+=1
	if (tag == "O"):
		if (re.match(regex, word)):
			countO[0]+=1
		else:
			countO[1]+=1

print "I Positive: " + str(countI[0]/(countI[1]+countI[0]))
print "I Negative: " + str(countI[1]/(countI[1]+countI[0]))
print "=================="
print "B Positive: " + str(countB[0]/(countB[1]+countB[0]))
print "B Negative: " + str(countB[1]/(countB[1]+countB[0]))
print "=================="
print "O Positive: " + str(countO[0]/(countO[1]+countO[0]))
print "O Negative: " + str(countO[1]/(countO[1]+countO[0]))