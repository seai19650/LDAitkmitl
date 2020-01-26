import sys
sys.path.append("..") # Adds higher directory to python modules path.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PDFreader.pdfReader import extract_pdf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import natsort 
import re
from pythainlp.word_vector import *

import docx2txt
from data_prepare import split_word, cut_character, postag, add_frequency

print("========== PART 1 : Input Files ==========")
def open_file(doc_path_dict):
    """
    Finding file in input path file and keep in dictionary
    """
    files = []
    data = {}
    data_file =[]
    for proj_id in doc_path_dict.keys():
        files.append(doc_path_dict[proj_id])
    files = natsort.natsorted(files,reverse=True)
    print(files)
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
    return data

#set path here
doc_path_dict = {'RDG5430015':'document/docx/RDG5430015.docx', 
'RDG5430002':'document/docx/RDG5430002.docx',
'RDG5250070':'document/docx/RDG5250070.docx',
'MRG5980259':'document/docx/MRG5980259.docx',
'MRG5980243':'document/docx/MRG5980243.docx',
'NationalStrategies_20y':'document/docx/NationalStrategies_20y.docx'}
# Append ออวน to document
doc_path_dict['ยุทธศาสตร์_อววน_v12_ไม่มีผนวก'] = 'document/docx/ยุทธศาสตร์_อววน_v12_ไม่มีผนวก.docx'
# path = 'document/docx'
data = open_file(doc_path_dict)
num_doc = len(data)
# print(num_doc)

print("========== PART 2 : Data Preparation ==========")

# Set data into dataframe type
def to_dataframe(data):
    """
    Changing document in dictionary to dataframe and setting field like...
    | proj_id | file_path | content |

    proj_id: Document's file name.
    file_path: File path of document.
    content: Content of document.
    """
    data_doc = []
    # data_title = title
    data_content = []
    for proj_id in data.keys():
        data_content.append(data[proj_id][0])
        data_doc.append(proj_id)
        file_path = doc_path_dict[proj_id]
    data_df_dict = {'proj_id': data_doc, 'file_path':file_path,'content': data_content}
    data_df = pd.DataFrame.from_dict(data_df_dict)
    return data_df

data_df = to_dataframe(data)
# data_df.head()
print(data_df)

print("========== PART 3 : Creating Word Tokenize ==========")
# Word Tokenization
inp_list = []
for num in range(num_doc):
    content = data_df['content'][num]
    words = split_word(content)
    inp_list.append(words)

def sentence_vec(words: list, use_mean: bool = True):
    vec = np.zeros((1, 300))
    _MODEL = get_model()
    # use_mean = True
    for word in words:
        if word == " ":
            word = "xxspace"
        elif word == "\n":
            word = "xxeol"

        if word in _MODEL.wv.index2word:
            vec += _MODEL.wv.word_vec(word)
        else:
            pass

    if use_mean:
        vec /= len(words)

    # print(vec)
    return vec

doc_score = {}
for i in range(1,len(inp_list)):
    cos = cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[i]))
    doc_score[data_df['proj_id'][i]] = cos[0][0]
doc_ranking = {key: rank for rank, key in enumerate(sorted(doc_score, key=doc_score.get, reverse=True), 1)}
print(doc_score)
print(doc_ranking)

# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[1])))
# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[2])))
# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[3])))
# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[4])))
# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[5])))
# print(cosine_similarity(sentence_vec(inp_list[0]),sentence_vec(inp_list[6])))


# print("========== PART 4 : Term Weighting with TfidfVectorizer ==========")
# # Term Weighting with TfidfVectorizer
# inp_list_j = [','.join(tkn) for tkn in inp_list]
# # print(inp_list_j)
# tvec = TfidfVectorizer(analyzer=lambda x:x.split(','),)
# t_feat = tvec.fit_transform(inp_list_j)
# # print(t_feat)

# print("========== PART 5 : Measure the Cosine Similarity ==========")
# doc_score = {}
# # Measure the cosine similarity between the first document vector and all of the others
# max_cos = 0
# best_row = 0
# for row in range(1,t_feat.shape[0]):
#     cos = cosine_similarity(t_feat[0], t_feat[row])
#     # print(row, cos)
#     doc_score[data_df['proj_id'][row]] = cos[0][0]
#     # best so far?
#     if cos > max_cos:
#         max_cos = cos
#         best_row = row
# print("Most similar document was row %d: cosine similarity = %.3f" % ( best_row, max_cos ) )
# # Best document - just display the start of it
# # print(doc_score)
# doc_ranking = {key: rank for rank, key in enumerate(sorted(doc_score, key=doc_score.get, reverse=True), 1)}
# # print(doc_ranking)

# topic_similarity = []
# for proj_id in doc_score.keys():
#     sim_dict = {'ranking':doc_ranking[proj_id],
#                 'proj_proposal_id':proj_id,
#                 'file_path': doc_path_dict[proj_id],
#                 'score':doc_score[proj_id]}
#     topic_similarity.append(sim_dict)
# print(topic_similarity)




