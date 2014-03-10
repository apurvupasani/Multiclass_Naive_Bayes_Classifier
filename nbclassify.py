import os;
import glob;
import re;
import math;
import sys;
#Here I will do the following steps in order to ensure that the words are read from the dictionary
#Once again I will implement the WordClassifier class which will import the details from the model file and write the data into the dictionary
#Then I will open all the test data files and based on the text in the file,I will perform the naive bayes classification using the log maximum likelihood estimate for all types of document classifications and classify the files on the basis of highest cumulative probability

######################################################################

# Class used to store the word and its mapping

class WordMapping :

	def __init__(self,word,countsPerLabel,probabsPerLabel):
		self.word = word;
		self.countsPerLabel = countsPerLabel;
		self.probabsPerLabel = probabsPerLabel;
		
	
	def getDetails():
		return self;

class FScoreMatcher:
	def __init__(self,actualValue,classifiedValue):
		self.actualValue = actualValue;
		self.classifiedValue =classifiedValue;
	def getDetails():
		return self;
######################################################################

def prepareDictionary(fileName):
	dictionary = {};
	modelFile = open(fileName,'r');
	
	for line in modelFile:
		line  = line.rstrip('\n\r');
		if len(line) > 0 :
			if line.startswith('$') :
				continue;
			else:
				word = line.split('~##~')[0];
				classifiers = line.split('~##~')[1].split("|");
		
				countsPerLabel={};
				probabPerLabel={};
				for text in classifiers:
					classifierText = text.strip().split(' ');
					if len(classifierText) != 1: 
						countsPerLabel[classifierText[0]] = int(classifierText[1]);
						probabPerLabel[classifierText[0]] = float(classifierText[2]);
				wordMapping = WordMapping(word,countsPerLabel,probabPerLabel);
				dictionary[word] = wordMapping;

	return dictionary;
#####################################################################################


def prepareMetaDataInfo(fileName):
	metaData = {};
	modelFile = open(fileName,'r');
	
	for line in modelFile:
		line = line.rstrip('\n\r');
		if len(line)>0 and line.startswith('$'):

			if line.startswith('$LABEL##') :
				labels = line.strip().split("##")[1].split(' ');
				metaData['LABEL'] = labels;			
			elif line.startswith('$LABELCOUNT##') :
				labelCountsTemp = line.strip().split("##")[1].split(' ');
				labelCounts={};
				for l in range(0,len(labels)):
					labelCounts[labels[l]] = labelCountsTemp[l];	
				metaData['LABELCOUNT'] = labelCounts;	
			elif line.startswith('$WORDCOUNT##') :
				wordCountsTemp = line.strip().split("##")[1].split(' ');
				wordCounts={};
				for l in range(0,len(labels)):
					wordCounts[labels[l]] = wordCountsTemp[l];	
				metaData['WORDCOUNT'] = wordCounts;	
			elif line.startswith('$UNIQUEWORDCOUNT##') :
				uniqueCountsTemp = line.strip().split("##")[1].split(' ');
				uniqueCounts={};
				for l in range(0,len(labels)):
					uniqueCounts[labels[l]] = uniqueCountsTemp[l];	
			
				metaData['UNIQUECOUNT'] = uniqueCounts;	
	return metaData;		
##################################################################################

def getLabelTypes(dictionary):
	labelTypes = {};
	for word in dictionary:
		wordMapping = dictionary[word];
		for label in wordMapping.countsPerLabel:
			if label in labelTypes:
				continue;
			else:
				labelTypes[label] = label;
	return labelTypes;
################################################################################

def getTestDataFormatted(fileName):
	file = open(fileName,'r');
	generatedString ='';
	for line in file:
		re.sub(r'[&\s]',' ',line);
       	        generatedString += str(line.rstrip('\n\r'))+ ' ';
	return generatedString;	


def getTestStringFormatted(line):
	generatedString ='';
	re.sub(r'[&\s]',' ',line);
       	generatedString = str(line.rstrip('\n\r'));
	return generatedString;	

#################################################################################

# This is the most important method of the classifier. Here we do the following things,We first strip the data and convert it to upper text. Then we split the data into words. Then we loop over each word to find the probabality in each case(HAM/SPAM..etc). For this we first look at the word in the dictionary. If the word is in the dictionary, we simply take the appropriate label probablity, compute the log and add it to the counts. If the word is not present, we do add 1 smoothing and perform the same operation

def classifyText(testData,metadata,dictionary):

	testData = testData.strip().upper();

	labelTypes =  metadata['LABEL'];
	labelCounts = metadata['LABELCOUNT'];
	wordCounts = metadata['WORDCOUNT'];
	uniqueWordCounts = metadata['UNIQUECOUNT'];
	probabValues = metadata['PROBABVALUES'];

	logCount = {};

	for label in labelTypes:
		logCount[label] = math.log(probabValues[label]);

	splitTestData = testData.split(' ');

	for word in splitTestData:
	
		if word in labelTypes:
			continue;
		elif word in dictionary:
			wordMapping = dictionary[word];
			for label in logCount:
				logCount[label] += math.log(wordMapping.probabsPerLabel[label],10);
					
		else: # word is new
			
			for label in logCount:
				logCount[label] += math.log(float(1)/(float(wordCounts[label])+float(uniqueWordCounts[label])),10);
			
					
	return findMax(logCount);	


#################################################################################

def findMax(list):
	labels = '';
	value = -999999999999;
	for label in list:
		if(list[label]>value):
			value = list[label];
			labels = label;
	return labels;


#################################################################################
modelFileName = sys.argv[1].strip();
metadata = prepareMetaDataInfo(modelFileName);

labelMeta = metadata['LABEL'];
labelCountsMeta = metadata['LABELCOUNT'];
labelCounts={};
totalCount = 0;
for label in labelMeta:
	totalCount += int(labelCountsMeta[label]);
	
for label in labelMeta:
	labelCounts[label] = float(labelCountsMeta[label])/totalCount;

metadata['PROBABVALUES'] = labelCounts;

	
dictionary = prepareDictionary(modelFileName);


#print "Start classification process";

fileList ={};

fileName = open(sys.argv[2].strip(),'r');
counter = 0;
for line in fileName:
	generatedString = getTestStringFormatted(line);
	classifiedValue = classifyText(generatedString,metadata,dictionary);
	print classifiedValue;	
	#print str(counter) +" "+ line.split(' ')[0]+" "+classifiedValue;		
	#fileList[counter] = FScoreMatcher(line.split(' ')[0].strip(),classifiedValue);
	counter+=1;

#fscoreLabel = raw_input("Enter the label you want to find F-Score for: ");
#countCorrectLabel = 0;
#countTotalClassifiedLabel = 0;
#countTotalLabel = 0;

#for item in fileList:
#	fscoreMatcher = fileList[item];
	
#        if fscoreMatcher.actualValue ==fscoreLabel:
#		countTotalLabel+=1;
	
#        if fscoreMatcher.classifiedValue == fscoreLabel:
#		countTotalClassifiedLabel +=1;	
#		if fscoreMatcher.actualValue == fscoreMatcher.classifiedValue:
#			countCorrectLabel +=1;
#precision = float(countCorrectLabel)/countTotalClassifiedLabel;
#recall = float(countTotalClassifiedLabel)/countTotalLabel;

#fScore = 2*(precision*recall)/(precision+recall);

#print 'Precision is : '+str(precision);
#print 'Recall is : '+str(recall);
#print 'F-Score is : '+str(fScore);

