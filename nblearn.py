import sys;

######################################################################

class WordMapping :

	def __init__(self,word,countsPerLabel,probabsPerLabel):
		self.word = word;
		self.countsPerLabel = countsPerLabel;
		self.probabsPerLabel = probabsPerLabel;
		
	
	def getDetails():
		return self;

######################################################################

# This function is used to give the unique number of words in a particular type of classifier. The words are identitifed as case insensitive (meeting == Meeting == MeeTinG)
# Also 

def getUniqueCount(fileName,classifierPhrase):
	count = {};
	file = open(fileName,'r');
	for line in file : 
		if line.startswith(classifierPhrase):
			words = line.split(' ');
			for w in words:
			   if w.upper() in count:
				count[w.upper()]+=1;
			   else:
				count[w.upper()] = 1;


	return count;

######################################################################

######################################################################

# This function is responsible for getting the total line count of 
# a particular phrase . ie. check whether the phrase is there in line

def getNumCount(fileName,classifierPhrase):
	file = open(fileName,'r');
	count = 0;
	for line in file :
		if line.startswith(classifierPhrase) :
			count+=1;

	return count;
######################################################################

######################################################################
# This function takes the the file name,phrase and returns the total number of words in the line excluding the phrase

def getWordCount(fileName,classifierPhrase): 

	file = open(fileName,'r');
	count = 0;
	for line in file :
		if line.startswith(classifierPhrase) :
			count += (len(line.split(' ')) - 1);

	return count;

#####################################################################


######################################################################

def getLabelTypes(fileName):
	file = open(fileName,'r');
	count = 0;
	labelTypes = {};
	labelTypesOthers = {};
	for line in file:
#		print line;
		word = line.split(' ')[0];
		if word in labelTypes:
			continue;
		else:
			labelTypes[word]=word;
	
	for word in labelTypes:
		labelTypesOthers[count] = labelTypes[word];
		count+=1;
	return labelTypesOthers;

################################################################################

##################################################################################

# This function creates a new wordmapping object. It sets the prior probabilities of the word given label.Also it initializes the prior probabilities of rest of the labels in case they need to be updated in future

def createNewWordMapping(labelTypes,label,word,times,titalWordCounts,uniqueWordsPerLabel):
	
	countDictionary = {};
	probabDictionary = {};
	countDictionary[label] = times + 1;
	probabDictionary[label] = float(countDictionary[label]) / (totalWordCounts[label] + len(uniqueWordsPerLabel[label]));
	for labelOther in labelTypes : 
		if labelTypes[labelOther] is label:
			continue;
		else:
			countDictionary[labelTypes[labelOther]] = 1;
			probabDictionary[labelTypes[labelOther]] = float(countDictionary[labelTypes[labelOther]]) / (totalWordCounts[labelTypes[labelOther]] + len(uniqueWordsPerLabel[labelTypes[labelOther]]));
		
	wordMapping = WordMapping(word,countDictionary,probabDictionary);
	return wordMapping;
######################################################################################


# Here we fetch the training file name from which we have to get the #messages
fileName = sys.argv[1];
labelTypes = getLabelTypes(fileName);
#print labelTypes;
######################################################################

# Here we invoke the function to fetch the total number of SPAM and #HAM messages there may exist
totalLabelCounts = {};

for label in labelTypes: 
	totalLabelCounts[labelTypes[label]] =  getNumCount(fileName,labelTypes[label]);

#print totalLabelCounts;


#####################################################################

#Here we calculate the probability of message being HAM or SPAM

probabalityOfMessageBeingLabel = {};

totalCounts = 0;
for label in labelTypes:
	totalCounts += totalLabelCounts[labelTypes[label]];
#print totalCounts;

for label in labelTypes:
	probabalityOfMessageBeingLabel[labelTypes[label]] = float(totalLabelCounts[labelTypes[label]])/(totalCounts);

#print probabalityOfMessageBeingLabel;

######################################################################

# Now we have to find the total number of words there are in HAM messages and number of messages in SPAM

totalWordCounts = {};
for label in labelTypes: 
	totalWordCounts[labelTypes[label]] =  getWordCount(fileName,labelTypes[label]);

#print totalWordCounts;


# This is extremely important for finding the prior probablities for words given message to be spam

#####################################################################

# Now create a local dictionary of words. We create a class with following field for defining the word and its probabilities. Then we will define a set of wrapper methods to store the dictionary into a model file and fetch data back into dictionary.

# Following fields are to be captured : word name, count(SPAM), count(HAM), P(Word/SPAM), P(Word/HAM)

# Here we fetch all the words which are there in HAM and SPAM training sets. This is good because of 2 reasons :
# 1. We need to find the probability of each words and the collection of both is exhaustive
# 2. We  need the count of unique words for add-1 smoothening

uniqueWordsPerLabel = {};
for label in labelTypes: 
	uniqueWordsPerLabel[labelTypes[label]] =  getUniqueCount(fileName,labelTypes[label]);

# Now we start the process of filling the dictionary
# This has to be done very carefully. There may be many lists contain the count of occcurence of the word. There also exist an intersection of common words. 
# We start with first label set. Initially the dictionary is empty. We start creating the dictionary object and initialize the rest of label values to 1 and assign add-1 smoothening probabality even to other label dataset (remember, the word might not come in SPAM data set)
# Once we are done with first dataset, we look at other dataset. Here we have to be extremely careful in the sense that we have to update the values wherever, we can.
#Once we are done with all datasets, we invoke the method to write the data into the dictionary.
#And we are done.

# Declare the dictionary

dictionary = {};

# Begin with the first label to get things started 

for word, times in uniqueWordsPerLabel[labelTypes[0]].items():
	wordMapping = createNewWordMapping(labelTypes,labelTypes[0],word,times,totalWordCounts,uniqueWordsPerLabel);

	dictionary[word] = wordMapping;

# Beginning with rest of the data set

for label in labelTypes:
	
	if labelTypes[label] is labelTypes[0]:
		continue;
	else:

		for word, times in uniqueWordsPerLabel[labelTypes[label]].items():
	
			if word in dictionary :
			
				wordMapping = dictionary[word];
				wordMapping.countsPerLabel[labelTypes[label]] += times;
				wordMapping.probabsPerLabel[labelTypes[label]] = float(wordMapping.countsPerLabel[labelTypes[label]]) /(totalWordCounts[labelTypes[label]] + len(uniqueWordsPerLabel[labelTypes[label]]));
			else:
				
				wordMapping = createNewWordMapping(labelTypes,labelTypes[label],word,times,totalWordCounts,uniqueWordsPerLabel);

				dictionary[word] = wordMapping;


# Now write the details into the model file 
# Format : <Word>~<Label> <CountHAM> <ProbabHAM>|<Label> <CountSPAM> <ProbabHAM>| ..

modelFile = open(sys.argv[2].strip(),'w');
totalLabelString = "$LABEL##";
for label in labelTypes:
	totalLabelString += labelTypes[label]+' ';
totalLabelString +='\n';
modelFile.write(totalLabelString);

totalLabelCountString="$LABELCOUNT##";
for label in totalLabelCounts:
	totalLabelCountString += str(totalLabelCounts[label])+' ';
totalLabelCountString +='\n';
modelFile.write(totalLabelCountString);

totalWordCountString = "$WORDCOUNT##";
for label in totalWordCounts:	
	totalWordCountString += str(totalWordCounts[label])+ ' ';
totalWordCountString +='\n';
modelFile.write(totalWordCountString);

uniqueWordCountString = "$UNIQUEWORDCOUNT##";
for label in uniqueWordsPerLabel:	
	uniqueWordCountString += str(len(uniqueWordsPerLabel[label]))+ ' ';
uniqueWordCountString +='\n';
modelFile.write(uniqueWordCountString);

for word in dictionary:
	wordMapping = dictionary[word];
	writeString = wordMapping.word+"~##~";
	
	for label in labelTypes:
		writeString += labelTypes[label] + ' '+str(wordMapping.countsPerLabel[labelTypes[label]])+' '+str(wordMapping.probabsPerLabel[labelTypes[label]])+"|";
	modelFile.write(writeString+'\n');


	
	
modelFile.close();

print 'Model File Created';



	 


