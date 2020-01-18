import sys
sys.path.append("..") # Adds higher directory to python modules path.

from pythainlp import word_tokenize
from pythainlp.corpus import thai_words, thai_stopwords, thai_syllables
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from gensim.models import LsiModel, LdaModel, CoherenceModel
from pylexto import LexTo
from PDFreader.pdfReader import extract_pdf
import string
import pythainlp.corpus
import pyLDAvis.gensim
import os
import random
import pandas as pd
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import re

import docx2txt
from data_prepare import split_word, cut_character, postag, add_frequency
from distribution import topicTerm_dist,docTopic_dist,Ndoc_topic

print("========== PART 1 : Input Files ==========")
def open_file(path):
    """
    Finding file in input path file and keep in dictionary
    """
    files = []
    data = {}
    data_file =[]
    for r, d, f in os.walk(path):
        for file in f:
            #Text file
            if 'news.txt' in file:
                files.append(os.path.join(r, file))
#             elif file.endswith('.pdf'):
#                 print(file)
#                 files.append(os.path.join(r, file))
            elif '.docx' in file:
                print(file)
                files.append(os.path.join(r, file))
                
    #Find file in folder path and extract file to text
    for f in files:
        f_list = re.split("; |/|\\.",f)
        if f.endswith('.pdf'):
            data_file_text = extract_pdf(f)
        elif f.endswith('.docx'):
            data_file_text = docx2txt.process(f)
        try:
            data_file.append(data_file_text)
        except:
            print("=======ERROR=======")
            print(f, f_list)
            print('+++++++++++++++++++')

#       Add Topic in dict
        data[f_list[-2]] = [str(data_file_text)]

        #create rd_list for create training data
#         data_file_text.close()
    return data

#set path here
path = 'document/docx'
data = open_file(path)
#get input title here
title = ['ผลกระทบของเอนโซ่ต่อการผันแปรของมรสุมตะวันตกเฉียงใต้ในรอบปีบริเวณประเทศไทย', 
          'การฟื้นฟูป่าชายเลนบ้านเปร็ดในโดยการมีส่วนร่วมของชุมชนฯ', 
          'ร่างยุทธศาสตร์',
          'การพัฒนาประสิทธิภาพการอบยางล้อ', 
          'การตรวจสอบและเตรียมความพร้อมโรงพยาบาลในพื้นที่เสี่ยงภัยแผ่นดินไหว:บทเรียนจากแผ่นดินไหวแม่ลาว', 
          'ฤทธิ์ในการต้านการอักเสบและกดภูมิคุ้มกันของกรดวานิลลิคและการพัฒนาตำรับที่เหมาะสมสำหรับส่งผ่านทางผิวหนัง']
num_doc = len(title)


print("========== PART 2 : Data Preparation and Creating Word Tokenize ==========")

# Set data into dataframe type
def to_dataframe(data):
    """
    Changing document in dictionary to dataframe and setting field like...
    | doc_id | title | content |

    doc_id: Document's file name.
    title: Tile of document.
    content: Content of document.
    """
    data_doc = []
    data_title = title
    data_content = []
    for doc_id in data.keys():
        data_content.append(data[doc_id][0])
        data_doc.append(doc_id)
    data_df_dict = {'doc_id': data_doc, 'title': data_title, 'content': data_content}
    data_df = pd.DataFrame.from_dict(data_df_dict)
    return data_df

data_df = to_dataframe(data)
data_df.head()

inp_list = []
for num in range(num_doc):
    content = data_df['content'][num]
    inp_list.append(split_word(content))

count = 0
for word in inp_list:
    count += len(word)
print(count)

# Create dictionary, corpus and corpus TFIDF
# Turn tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(inp_list)
dict2 = {dictionary[ID]:ID for ID in dictionary.keys()}

# Convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in inp_list]
tfidf = models.TfidfModel(corpus, smartirs='ntc')
corpus_tfidf = tfidf[corpus]

# Remove character number is less than 2 words off
num_cut = 2
new_lists = cut_character(inp_list, num_cut)

# Remove word is not noun and prop noun by pos_tag function
for num in range(num_doc):
    new_lists[num] = postag(new_lists[num])

# Create new dict and corpus
dictionary2 = corpora.Dictionary(new_lists)
dict_2 = {dictionary2[ID]:ID for ID in dictionary2.keys()}
corpus2 = [dictionary2.doc2bow(text) for text in new_lists]

# Header Title plus frequency in corpus
corpus2 = add_frequency(dict_2, corpus2, data_df, 10, num_doc)

print("========== PART 3 : Generate LDA Model ==========")
# Generate LDA Model
def LDAmodel(dictionary, corpus, num_top):
    ldamodel = LdaModel(corpus, num_top, id2word = dictionary, decay=0.6, random_state = 2, passes = 10)
    return ldamodel

# Default number of topic is 10. If number of document is less than 10, will be used to number of topic.
num_top = 10
if num_doc <= 10:
    num_top = num_doc

ldamodel = LDAmodel(dictionary2, corpus2, num_top)
term_dist_topic = ldamodel.show_topics(num_top, 1000, log=True, formatted=False)
# print(term_dist_topic)

print("========== PART 4 : Topic-term distribution ==========")
### Topic-Term Dist
topic_term_dist = []
topic_term_dist = topicTerm_dist(topic_term_dist, term_dist_topic)
print(topic_term_dist)

print("========== PART 4-1 : Document-topic (all) distribution ==========")
### Doc_topic_all_dist
doc_topic_dist = []
doc_topic_dist = docTopic_dist(doc_topic_dist, data_df, num_doc, inp_list,dictionary2,ldamodel)
print(doc_topic_dist)

print("========== PART 4-2 : Topic-term (min) distribution ==========")
### Doc_topic_min_dist
n_doc_intopic = []
n_doc_intopic = Ndoc_topic(n_doc_intopic,num_doc, data_df, inp_list, dictionary2, ldamodel)
print(n_doc_intopic)

# Generate LSI Model
def LSImodel(dictionary, corpus_tfidf, num_top=6):
    lsimodel = LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_top, decay=0.5)
    return lsimodel


lsimodel = LSImodel(dictionary2, corpus2, 6)

# lsimodel.show_topics(6, 10, log=True, formatted=False)

print("========== PART 5 : Evaluate Model ==========")
# Evaluate
lsi_coherence = CoherenceModel(lsimodel, corpus=corpus_tfidf, dictionary=dictionary2, coherence='u_mass')
lda_coherence = CoherenceModel(ldamodel, corpus=corpus2, dictionary=dictionary2, coherence='u_mass')
print(lda_coherence.get_coherence_per_topic())
print("LDA umass score = %.4f , LSI umass score = %.4f"% (lda_coherence.get_coherence(), 
                                                          lsi_coherence.get_coherence()))

lsi_coherence = CoherenceModel(lsimodel, texts=new_lists, dictionary=dictionary2, coherence='c_uci')
lda_coherence = CoherenceModel(ldamodel, texts=new_lists, dictionary=dictionary2, coherence='c_uci')
print("LDA uci score = %.4f , LSI uci score = %.4f"% (lda_coherence.get_coherence(), 
                                                      lsi_coherence.get_coherence()))

print("========== PART 6 : Export pyLDAvis HTML ==========")
import pyLDAvis.gensim
# pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(ldamodel, corpus2, dictionary=ldamodel.id2word)
pyLDAvis.save_html(vis, "docx_LDAvis_newmm_2n_postag_title_10n.html")
# vis


