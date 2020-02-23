import re
from PDFreader import pdfReader
import docx2txt

# This package is for parsing a file name
import ntpath

import os

"""
    A Utility (Util) class acts like a collection of methods to handles file management, loading and saving. 
    This class contains 4 static methods, including: 
        1) read_file()
        2) find_read_file()
        3) filter_file_to_read()
        4) path_leaf()
"""


class Util:
    """
        This class has not either instance or static attributes
    """

    """
      A static method, read_file(files), reads all files listed in a given List
    
    Parameters
    ----------
    files: a list of files in a string format, required
        
    Returns
    ----------
    data: a dictionary, in which a key is a file name and a value is a document text (raw text.)
        {
            "SRI61X0602_full": "การศึกษาวิเคราะห์การทุจริตคอร์รัปชันของขบวนการเครือข่ายนายหน้าข้ามชาติในอุตสาหกรรมประมงต่อเนื่องของประเทศไทย",
            "RDG6140010_full": "โครงการวิจัยและพัฒนาแนวทางการหนุนเสริมทางวิชาการเพื่อพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา",
            ...
        }
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

    # @staticmethod
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

    """
    A static method, filter_file_to_read(local_path, files), filters 'in' files in supported formats only (pdf, docx)
    
    Parameters
    ----------
    local_path: a local path that all files are storedt and located
    
    files: a list of files in a string format, required
        
    Returns
    ----------
    data: a dictionary, in which a key is a file name and a value is a document text (raw text.)
        {
            "SRI61X0602_full": "การศึกษาวิเคราะห์การทุจริตคอร์รัปชันของขบวนการเครือข่ายนายหน้าข้ามชาติในอุตสาหกรรมประมงต่อเนื่องของประเทศไทย",
            "RDG6140010_full": "โครงการวิจัยและพัฒนาแนวทางการหนุนเสริมทางวิชาการเพื่อพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา",
            ...
        }
    """
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
                print(
                    '-- Only pdf and docx formats are supported. This file will be ignored due to not support types: \"{0}\". --'.format(
                        file))
        data = Util.read_file(to_read_files)
        return data

    """
    A static method, path_leaf(path), returns a file name (leaf) from a given url
    
    Parameters
    ----------
    path: a path or url directing to a file 
        
    Returns
    ----------
    tail: a file name (leaf of path)
    """
    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
