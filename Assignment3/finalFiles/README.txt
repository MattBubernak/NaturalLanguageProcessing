Authors: Matt Bubernak, Harsha Phadke
Date: 4/24/2015
Purpose: IOB tagging

Files Included: 
===============
* ubernak_Phadke_IOBTagger.py (IOB tagger)
* regexChecker.py (Used for testing regexes)
* grabLinesWithLetter.py (Used for extracting word-tag groups)

Usage Instruction(ubernak_Phadke_IOBTagger.py): 
==================
The following line of code will generate a test output based on a set of training data, and test data, that includes a copy of the test data labeled with IOB tags generated based on trainig from the training data file.
"python Bubernak_Phadke_IOBTagger.py [PathToInputTrainingData.txt] [PathToInputTestData.txt] [PathToOutputFile.txt]"

Usage Instruction(grabLinesWithLetter.py): 
==================
The following line will take a file that contains words and IOB tags and generate an output file that contains all lines tagged with the user input "letter". 
"python grabLinesWithLetter.py [inFile.txt] [letter]"

Usage Instruction(regexChecker.py): 
==================
The following line will read in a line of words with IOB tags and return how many times a given regex(defined in the file) matches each IOB tag. It specifies the percent it matches yes/no for each type of tag. Used for measuring the effectiveness of different possible features. 
"python regexChecker.py [PathToInputData.txt]"


