import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Util import Util
from TextPreProcessing import TextPreProcessing
from TextDistribution import TextDistribution

from pythainlp import word_tokenize
from pythainlp.corpus import thai_words, thai_stopwords, thai_syllables
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from gensim.models import LsiModel, LdaModel, CoherenceModel
from pylexto import LexTo

import string
import pythainlp.corpus
import pyLDAvis.gensim

import random
import pandas as pd
import sklearn
import numpy as np
import matplotlib.pyplot as plt


import os


# This package is for downloading pdf
import urllib.request



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


# todo edit "Create a new classifier which is based on the sckit-learn BaseEstimator and ClassifierMixin classes"
class LDAModeling:

    #def __init__(self):

    def to_dataframe(self, data, titles):
        """
        Changing document in dictionary to dataframe and setting field like...
        | doc_id | title | content |

        doc_id: Document's file name.
        title: Tile of document.
        content: Content of document.
        """
        data_doc = []
        data_titles = titles
        data_content = []
        for doc_id in data.keys():
            data_content.append(data[doc_id][0])
            data_doc.append(doc_id)
        data_df_dict = {'doc_id': data_doc, 'title': data_titles, 'content': data_content}
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

    def perform_topic_modeling(self, input_local_root, files, titles, output_dir, pyLDAvis_output_file, max_no_topics = 10):

        print("========== PART 1 : Input Files ==========")
        data = Util.filter_file_to_read(input_local_root, files)
        num_doc = len(titles)

        print("========== PART 2 : Data Preparation and Creating Word Tokenization ==========")
        # Set data into dataframe type
        data_df = self.to_dataframe(data, titles)
        data_df.head()

        inp_list = []
        for num in range(num_doc):
            content = data_df['content'][num]
            inp_list.append(TextPreProcessing.split_word(content))

        counter = 0
        for word in inp_list:
            counter += len(word)
        print("Unique words in this processing corpus: " + counter)

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
        new_lists = TextPreProcessing.cut_character(inp_list, num_cut)

        # Remove word is not noun and prop noun by pos_tag function
        for num in range(num_doc):
            new_lists[num] = TextPreProcessing.postag(new_lists[num])

        # Create new dict and corpus
        dictionary2 = corpora.Dictionary(new_lists)
        dict_2 = {dictionary2[ID]:ID for ID in dictionary2.keys()}
        corpus2 = [dictionary2.doc2bow(text) for text in new_lists]

        # Header Title plus frequency in corpus
        corpus2 = TextPreProcessing.add_frequency(dict_2, corpus2, data_df, 10, num_doc)

        print("========== PART 3 : Generate LDA Model ==========")
        # Generate LDA Model


        # Default number of topic is 10. If the number of documents is fewer than the maximum number of topics, the number of documents will be used to as the maximum number of topics.
        # if num_doc <= 10:
        #     max_no_topics = num_doc
        max_no_topics = min([max_no_topics, num_doc])

        ldamodel = self.LDAmodel(dictionary2, corpus2, max_no_topics)
        term_dist_topic = ldamodel.show_topics(max_no_topics, 1000, log=True, formatted=False)
        print(term_dist_topic)

        print("========== PART 4 : Topic-term distribution ==========")
        ### Topic-Term Dist
        topic_term_dist = []
        topic_term_dist = TextDistribution.topicTerm_dist(topic_term_dist, term_dist_topic)
        print(topic_term_dist)

        print("========== PART 4-1 : Document-topic (all) distribution ==========")
        ### Doc_topic_all_dist
        doc_topic_dist = []
        doc_topic_dist = TextDistribution.docTopic_dist(doc_topic_dist, data_df, num_doc, inp_list,dictionary2,ldamodel)
        print(doc_topic_dist)

        print("========== PART 4-2 : Topic-term (min) distribution ==========")
        ### Doc_topic_min_dist
        n_doc_intopic = []
        n_doc_intopic = TextDistribution.Ndoc_topic(n_doc_intopic,num_doc, data_df, inp_list, dictionary2, ldamodel)
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
        pyLDAvis.save_html(vis, output_dir + pyLDAvis_output_file)
        # vis

"""
    1) download all files from a list of URLs and save to local (API server)
    require:
        local_path = "/Users/Kim/Documents/TestDownloadFiles/"
"""
# todo change these three variables
# define a local root to save files
input_local_root = '/Users/Kim/Documents/trf_dir/TestDownloadFiles/'
# define an output directory to save pyLDAvis html file
output_dir = '/Users/Kim/Documents/trf_dir/PyLDAVizOutput/'
# define an output directory to save pyLDAvis html file
pyLDAvis_output_file = 'docx_LDAvis_newmm_2n_postag_title_10n.html'

urls = ['https://elibrary.trf.or.th/fullP/SRI61X0602/SRI61X0602_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6240001/RDG6240001_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6210003/RDG6210003_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140033/RDG6140033_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140024/RDG6140024_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140012/RDG6140012_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140022/RDG6140022_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140023/RDG6140023_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG60H0018/RDG60H0018_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6140010/RDG6140010_full.pdf']

titles = ['การศึกษาวิเคราะห์การทุจริตคอร์รัปชันของขบวนการเครือข่ายนายหน้าข้ามชาติในอุตสาหกรรมประมงต่อเนื่องของประเทศไทย',
            'นวัตกรรมเพื่อพัฒนาท้องถิ่นตามแนวทางปรัชญาของเศรษฐกิจพอเพียง: กรณีศึกษาองค์กรปกครองส่วนท้องถิ่นในจังหวัดนครสวรรค์และอุทัยธานี',
            'การศึกษาผลประโยชน์ทางธุรกิจที่เกิดจากการนำเศษพลอยมาใช้ประโยชน์ในเชิงพาณิชย์มากขึ้น',
            'การศึกษาประสบการณ์การเรียนรู้ของเยาวชนกลุ่มชาติพันธุ์ในการสร้างความรู้ด้านนิเวศวัฒนธรรม ',
            'การวิจัยและพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา ระบบพี่เลี้ยง และการวิจัยเป็นฐานของคณะครุศาสตร์ มหาวิทยาลัยราชภัฏ ปีที่ 2',
            'การพัฒนาชุดการเรียนรู้วิชาศิลปะในชั้นเรียนแบบเรียนรวมที่มีนักเรียนตาบอดระดับมัธยมศึกษาตอนปลายและการทดลองขยายผล',
            'การวิจัยและพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตปัญญาศึกษา การเป็นพี่เลี้ยงและการวิจัยเป็นฐาน ภาคกลาง-ภาคตะวันตก  ปีที่ 2 ',
            'ระบบและกระบวนการผลิตและพัฒนาครูโดยใช้โครงงานฐานวิจัย ในพื้นที่ภาคใต้ ปีที่ 2',
            'การศึกษาประวัติศาสตร์สังคมพหุวัฒนธรรมจากตำนานประวัติศาสตร์ท้องถิ่นภาคใต้',
            'โครงการวิจัยและพัฒนาแนวทางการหนุนเสริมทางวิชาการเพื่อพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา ระบบพี่เลี้ยง และการวิจัยเป็นฐานของคณะครุศาสตร์ มหาวิทยาลัยราชภัฏ']


print('========== Beginning file download with urllib2. ==========')
to_process_files = []
abs_file_paths = []
counter = 0;
for url in urls:
    file = Util.path_leaf(url)
    abs_file_path =  input_local_root + file
    #print(abs_file_path)

    if not os.path.isfile(abs_file_path):
        try:
            print('downloading file from this url: \"{0}\" with this file name : \"{1}\".'.format(url, file))
            urllib.request.urlretrieve(url, abs_file_path)
        except:
            print('An exception occurred when downloading a file from this url, \"{0}\"'.format(url))
            # Delete the title of a file that cannot be downloaded at a specific index.
            # This is to keep two lists of abs_file_paths and titles consistent.
            del titles[counter]

    else:
        print('-- This file, \"{0}\", already exists in: \"{1}\"! Therefore, this file will not be downloaded. --'.format(file, input_local_root))
    to_process_files.append(file)
    counter += 1;

ldamodeling = LDAModeling()
ldamodeling.perform_topic_modeling(input_local_root, to_process_files, titles,
                                   output_dir, pyLDAvis_output_file,
                                   max_no_topics = 6)


