#Filename: evalPOS.py
#Updated by: Matt Bubernak

import sys;

if len(sys.argv)!=3:
	print 'Usage: python evalPOS.py goldPOS_filename systemPOS_filename'
	sys.exit(1)

gold = [line.strip() for line in open(sys.argv[1], 'r')]
system = [line.strip() for line in open(sys.argv[2], 'r')]

if len(gold)!=len(system):
	print'"number of lines between gold and system do not match!'
	sys.exit(1)

tagCnt = 0
correctCnt = 0
tagInfo = {}
# For each line of the file 
for i in range(0,len(gold)):
	# If it's not the gold copy
	if not gold[i]:
		continue
	tagCnt+=1 # Incrament the tag count

	# Split the line on a tab
	goldPOS = gold[i].split('\t')[1]
	systemPOS = system[i].split('\t')[1]

	# Add the GOLD tag to our dictionary
	if (goldPOS in tagInfo):
		tagInfo[goldPOS]['total'] += 1
	else:
		tagInfo[goldPOS] = {}
		tagInfo[goldPOS]['total'] = 1
		tagInfo[goldPOS]['correct'] = 0
		tagInfo[goldPOS]['percent'] = 0

	# If it's not the user copy
	if not system[i]:
		continue
	# Check if the POS matches 
	elif goldPOS != systemPOS:
		continue

	correctCnt+=1
	tagInfo[goldPOS]['correct'] += 1
	tagInfo[goldPOS]['percent'] = 100.0*tagInfo[goldPOS]["correct"]/tagInfo[goldPOS]["total"]

worstTag = "NULL"
worstPercent = 100.00
print "All Tag Counts"
print "==="
for tag in tagInfo:
	if (tag != "."):
		print "Tg:" + tag + "\tTOTAL: " + str(tagInfo[tag]["total"]) + "\tCORRECT: " + str(tagInfo[tag]["correct"]) + "\tPERCENT CORRECT: " + str(tagInfo[tag]["percent"])
		if (tagInfo[tag]['percent'] < worstPercent):
			worstPercent = tagInfo[tag]['percent']
			worstTag = tag
if (worstTag != "NULL"):
	print "==="
	print 'Worst Tag: ' + worstTag + ". Correctly identified " + str(worstPercent) + " percent of the time"
print "==="
print 'Overall accuracy: %f%% %d/%d correct POS tags' % (100.0*(correctCnt)/tagCnt, correctCnt, tagCnt)
