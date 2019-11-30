# pdfreader
from pylexto import LexTo
from PDFreader.pdfReader import extract_pdf

#docx2xt
import docx2txt

from split_word import split_word 
import matplotlib.pyplot as plt
from clean_doc import clean_alphabet

from gensim import corpora, models

print("========== PART 1 : Input Dataset ==========")
data_file = []
data_file.append('FinalReport_Sample/pdf/RDG56A030_full.pdf') 
data_file.append('FinalReport_Sample/pdf/RDG60T0048V01_full.pdf') 

# Checking format file
for i in range(len(data_file)):
    if data_file[i].endswith('.pdf'):
        print("Document",i+1, " is pdf file.")
        print("filename:", data_file[i])
        # pdf document
        data_file[i] = extract_pdf(data_file[i])
    elif data_file[i].endswith('.docx'):
        print("Document",i+1, " is docx file.")
        # docx document
        data_file[i] = docx2txt.process(data_file[i])

print("========== PART 2 : Cleaning Data and Creating Word Tokenize ==========")
data_ready = []
for i in range(len(data_file)):
    print("------- Document",i+1,"-----------")
    # Cleaning document which have special alphabet 
    cleaned_data = clean_alphabet(data_file[i])
    # Split word in document
    data_ready.append(split_word(cleaned_data))
    # print("-------------------------")

print("========== PART 3 : Bag of word ==========")
# turn our tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(data_ready)
dict2 = {dictionary[ID]:ID for ID in dictionary.keys()}

wordid = []
word_origin = []
for ID in dictionary.keys():
    wordid.append(ID)
    print(ID, dictionary[ID])
    word_origin.append(dictionary[ID])

# convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in data_ready]
print("Corpus: ",corpus)

counts = {}
# process filtered tokens for each document
for doc_tokens in data_ready:
    for token in doc_tokens:
        # increment existing?
        if token in counts:
            counts[token] += 1
        # a new term?
        else:
            counts[token] = 1
# print("Found %d unique terms in this corpus" % len(counts))
# print(counts)

import operator
sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
# print(sorted_counts)
word_list = []
count_list = []
for word, count in sorted_counts:
    word_list.append(word)
    count_list.append(count)

import pandas as pd 
df= pd.DataFrame({"wordToken":word_list, "wordCount":count_list}) 

# print(df, "\n") 

# --------- Identify outliers with interquartile range (IQR) ----------
from numpy import percentile
data = df['wordCount']

# Calculate interquartile range
q25, q75 = percentile(data, 25), percentile(data, 75)
iqr = q75 - q25
# print('Percentiles: 25th=%.3f, 75th=%.3f, IQR=%.3f' % (q25, q75, iqr))

# Calculate the outlier cutoff
cut_off = iqr * 1.5
lower, upper = q25 - cut_off, q75 + cut_off

# Identify outliers
outliers = [x for x in data if x < lower or x > upper]
# print('Identified outliers: %d' % len(outliers))

# Remove outliers
outliers_removed = [x for x in data if x >= lower and x <= upper]
# print('Non-outlier observations: %d' % len(outliers_removed))

import numpy as np
outlier_u = np.unique(np.array(outliers))
df1 = df
for i in outlier_u:
    df1['wordCount'] = df1['wordCount'].replace(to_replace=i, value=np.nan)

df1 = df1.dropna()
counts = []
words = df1['wordToken'].values.tolist()
words_id = []
for num in range(0, len(word_origin)):
    for word in words:
        if word == word_origin[num]:
            # print("Origin word: ",wordid[num], word_origin[num])
            words_id.append(wordid[num])
            counts.append(df1['wordCount'].loc[df1['wordToken'] == word_origin[num]].values[0])

zipbObj = zip(words_id, counts)
list_ = list(zipbObj)
print([list_])

print("=======================")
# print(dictionary.keys())
# print(type(corpus))

