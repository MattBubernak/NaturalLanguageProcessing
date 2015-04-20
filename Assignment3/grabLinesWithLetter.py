#!/usr/bin/env python

import os, sys
import re

inFile = sys.argv[1]
letter = sys.argv[2]
outFile = inFile[:-4] + "_" + letter + ".txt" #str(sys.arvg[1]) + "_I"
print outFile

f1 = open(inFile)
lines = f1.readlines()
f2=open(outFile,'w')

for line in lines:
	if ("	" + letter in line):
		f2.write(line)

f1.close()
f2.close()
