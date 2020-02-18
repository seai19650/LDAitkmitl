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

"""An ensemble classifier that uses heterogeneous models at the base layer and a aggregation model at the 
    aggregation layer. A k-fold cross validation is used to generate training data for the stack layer model.

    Parameters
    ----------
    n_classes: integer, required (especially when setting proba_2train_meta = True)   
        The number of target classes for prediction, used to construct an array to store the prbability output from base classifiers

    estimators: list of BaseEstimators, optional (default = 6 base estimators, including:  
            1) DecisionTreeClassifier with max_depth = 10,
            2) ExtraTreeClassifier,
            3) LogisticRegression,
            4) Support Vector Machine - NuSVC,
            5) Support Vector Machine - SVC,
            6) KNeighborsClassifier with n_neighbors = 5)
        A list of scikit-learn base estimators with fit() and predict() methods.

    cv_folds: integer, optional (default = 5)
        The number of k to perform k-fold cross validation to be used. 

    proba_2train_meta: boolean, optional (default = False)
        A boolean flag variable to specify the meta learner at the stacked level should be trained either on label output or probability output.
            False => trained on 'label output' - Typical Super learner classifier, using Stack Layer Training Set (Labels)
            True => train on 'probability output' - using Stack Layer Training Set (Probabilities)

    ori_input_2train_meta: boolean , optional (default = False)
        A boolean flag variable to specify whether the meta learner should be trained on the training set with original features or not.
            False => trained only on 'output' from base estimators 
            True => train on 'original features/inputs' plus 'output' from base estimators

    meta_model_type: string, optional (default = "DCT")
        An option in string, only either "DCT" or "LR", to specify the type of model to use at the stack layer for a meta learner
            "DCT" => DecisionTreeClassifier
            "LR" => LogisticRegression

    est_accuracy: boolean, optional (default = False) - only available when proba_2train_meta = False
        A boolean flag variable to analyse and print the Mean Accuracy (MA) as the strength/performance of base estimators (predictive power). 
            False => do nothing
            True => analyse and print the mean accuracy

    est_corr: boolean, optional (default = False) - only available when proba_2train_meta = False
        A boolean flag variable to analyse and print the Pearson correlation between base estimators (diversity).
            False => do nothing
            True => analyse and print the Pearson correlation between base estimators

    debug_mode: boolean, optional (default = False)
        A boolean flag variable to set the verbose mode in printing debugging info via the "_print_debug" function

    Attributes
    ----------
    n_classes: integer   
        The number of target classes for prediction, used to expand an array to store the prbability output from base classifiers

    estimators: list
        A list of BaseEstimators used  

    cv_folds: integer
        the number of k to perform cross validation used 

    proba_2train_meta: boolean
        the flag variable to select the Stack Layer Training Set to be Labels (False) or Probabilities (True)

    ori_input_2train_meta: boolean
        the flag variable to include the original features/inputs in the Stack Layer Training Set: not include (False) or include (True)

    meta_model_type: string
        the option variable for the type of model of the meta-learner at the stack layer 

    est_accuracy: boolean
        the flag variable to perform and print an analysis of Mean Accuracy (MA) of base estimators: not perform (False) or perform (True)

    est_corr: boolean
        the flag variable to perform and print an analysis of Pearson correlation between base estimators: not perform (False) or perform (True)

    debug_mode: boolean
        The flag variable to print debugging info via the "_print_debug" function

    Notes
    -----


    See also
    --------

    ----------
    .. [1]  van der Laan, M., Polley, E. & Hubbard, A. (2007). 
            Super Learner. Statistical Applications in Genetics 
            and Molecular Biology, 6(1) 
            doi:10.2202/1544-6115.1309
    Examples
    --------
    >>> from sklearn.datasets import load_iris
    >>> from sklearn.model_selection import cross_val_score
    >>> clf = SuperLearnerClassifier()
    >>> iris = load_iris()
    >>> cross_val_score(clf, iris.data, iris.target, cv=10)

    """
# Create a new Utility class to for file management and loading
class Util:

    def __init__(self):
        self.data = {}

    def read_file(self, files):
        data_file = []

        # Read all given files in docx or readable pdf (readable means such a pdf file must be able to be read by pdfminer.)
        for f in files:
            #
            try:
                f_list = re.split("; |/|\\.", f)
                if f.endswith('.pdf'):
                    """
                        need modify here when the original file cannot be read.
                    """
                    data_file_text = extract_pdf(f)
                elif f.endswith('.docx'):
                    data_file_text = docx2txt.process(f)

                data_file.append(data_file_text)
            except:
                print("=======ERROR cannot fild the below file in a given path=======")
                print(f, f_list)
                print('+++++++++++++++++++')

            # Add Topic in dict
            self.data[f_list[-2]] = [str(data_file_text)]

            # create rd_list for create training data
        #         data_file_text.close()
        return self.data

    def find_read_file(self, path):

        # Find all files in a given input path and list absolute paths to them in the variable files
        files = []
        for r, d, f in os.walk(path):
            for file in f:
                # Text file
                if 'news.txt' in file:
                    files.append(os.path.join(r, file))
                #             elif file.endswith('.pdf'):
                #                 print(file)
                #                 files.append(os.path.join(r, file))
                elif '.docx' in file:
                    print(file)
                    files.append(os.path.join(r, file))

        data = self.read_file(files)
        return data

# Create a new classifier which is based on the sckit-learn BaseEstimator and ClassifierMixin classes
class LDAModeling:

    #def __init__(self):

    def to_dataframe(self, data, title):
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

    """to remove"""
    # Generate LDA Model
    def LDAmodel(self, dictionary, corpus, num_top=10):
        ldamodel = LdaModel(corpus, num_top, id2word=dictionary, decay=0.6, random_state=2, passes=10)
        return ldamodel

    """to remove"""
    # Generate LSI Model
    def LSImodel(self, dictionary, corpus_tfidf, num_top=6):
        lsimodel = LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_top, decay=0.5)
        return lsimodel

    def performTopicModeling(self):

        util = Util()
        print("========== PART 1 : Input Files ==========")
        path = 'document/docx'
        data = util.find_read_file(path)
        #get input title here
        # title = ['ผลกระทบของเอนโซ่ต่อการผันแปรของมรสุมตะวันตกเฉียงใต้ในรอบปีบริเวณประเทศไทย',
        #           'การฟื้นฟูป่าชายเลนบ้านเปร็ดในโดยการมีส่วนร่วมของชุมชนฯ',
        #           'ร่างยุทธศาสตร์',
        #           'การพัฒนาประสิทธิภาพการอบยางล้อ',
        #           'การตรวจสอบและเตรียมความพร้อมโรงพยาบาลในพื้นที่เสี่ยงภัยแผ่นดินไหว:บทเรียนจากแผ่นดินไหวแม่ลาว',
        #           'ฤทธิ์ในการต้านการอักเสบและกดภูมิคุ้มกันของกรดวานิลลิคและการพัฒนาตำรับที่เหมาะสมสำหรับส่งผ่านทางผิวหนัง']
        title = ['ผลกระทบของเอนโซ่ต่อการผันแปรของมรสุมตะวันตกเฉียงใต้ในรอบปีบริเวณประเทศไทย',
                  'การฟื้นฟูป่าชายเลนบ้านเปร็ดในโดยการมีส่วนร่วมของชุมชนฯ']
        num_doc = len(title)


        print("========== PART 2 : Data Preparation and Creating Word Tokenization ==========")

        # Set data into dataframe type
        data_df = self.to_dataframe(data, title)
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


        # Default number of topic is 10. If number of document is less than 10, will be used to number of topic.
        num_top = 10
        if num_doc <= 10:
            num_top = num_doc

        ldamodel = self.LDAmodel(dictionary2, corpus2, num_top)
        term_dist_topic = ldamodel.show_topics(num_top, 1000, log=True, formatted=False)
        print(term_dist_topic)

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




        lsimodel = self.LSImodel(dictionary2, corpus2, 6)

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




ldamodeling = LDAModeling()
ldamodeling.performTopicModeling()
