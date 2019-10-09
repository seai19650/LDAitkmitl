import re
import string
from pythainlp.word_vector import sentence_vectorizer 

def clean_documents(document):
    # ลบวงเล็บ
    document = re.sub(r'\(','', document)
    document = re.sub(r'\)','', document)
    document = re.sub(r'\[\n','', document)
    document = re.sub(r'\]\n','', document)
    
    # ลบ hashtag
    document = re.sub(r'\n','',document)
    
    #ลบ dash
    document = re.sub(r'-','',document)
    
    #ลบอักขระพิเศษ
    document = re.sub(r'§','',document)
    document = re.sub(r'■','',document)
    document = re.sub(r'”','',document)
    document = re.sub(r'“','',document)
    document = re.sub(r'‘','',document)
    document = re.sub(r'’','',document)
    
    # ลบ เครื่องหมายคำพูด (punctuation)
    for c in string.punctuation:
        document = re.sub(r'\{}'.format(c),' ',document)
    
    # ลบ separator เช่น \n \t
    document = ' '.join(document.split())
    
    return document
