import re
from PDFreader import pdfReader
import docx2txt

#This package is for parsing a file name
import ntpath

import os

"""
    A Utility (Util) class acts like a collection of methods to handles file management, loading and saving. 
    This class contains 4 static methods, including 
        1) read_file()
        2) find_read_file()
        3) filter_file_to_read()
        4) path_leaf()
"""
class Util:

    """
    Parameters
    ----------
    files: a list of string, required
        The number of target classes for prediction, used to construct an array to store the prbability output from base classifiers

    Returns
    ----------
    data: 


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
    """
    @staticmethod
    def read_file(files):
        # create a dictionary, in which a key is a file name and a value is a document text (raw text.)
        data = {}
        # Read all given files in docx or readable pdf (readable means such a pdf file must be able to be read by pdfminer.)
        for f in files:
            data_file_text = ""
            try:
                f_list = re.split("; |/|\\.", f)
                if f.endswith('.pdf'):
                    """
                        need modify here when the original file cannot be read.
                    """
                    data_file_text = pdfReader.extract_pdf(f)
                elif f.endswith('.docx'):
                    data_file_text = docx2txt.process(f)

                # Add document text in a dictionary
                data[f_list[-2]] = [str(data_file_text)]
            except:
                print("=======ERROR cannot find the below file in a given path=======")
                print(f, f_list)
                print('+++++++++++++++++++')

            # create rd_list for create training data
        #         data_file_text.close()
        return data

    #@staticmethod
    # def find_read_file(path):
    #
    #     # Find all files in a given input path and list absolute paths to them in the variable files
    #     files = []
    #     for r, d, f in os.walk(path):
    #         for file in f:
    #             # Text file
    #             if 'news.txt' in file:
    #                 files.append(os.path.join(r, file))
    #             elif file.endswith('.pdf'):
    #                 print(file)
    #                 files.append(os.path.join(r, file))
    #             elif '.docx' in file:
    #                 print(file)
    #                 files.append(os.path.join(r, file))
    #
    #     data = self.read_file(files)
    #     return data

    @staticmethod
    def filter_file_to_read(local_path, files):

        # Find all files in a given input path and list absolute paths to them in the variable files
        to_read_files = []
        for file in files:
            if file.endswith('.pdf'):
                print('-- To read file: \"{0}\". --'.format(file))
                to_read_files.append(local_path + file)
            elif file.endswith('.docx'):
                print('-- To read file: \"{0}\". --'.format(file))
                to_read_files.append(local_path + file)
            else:
                print('-- Only pdf and docx formats are supported. This file will be ignored due to not support types: \"{0}\". --'.format(file))
        data = Util.read_file(to_read_files)
        return data

    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)