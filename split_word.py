# pythainlp - word tokenize
from pythainlp.tokenize import word_tokenize
import pythainlp.corpus
from pythainlp.corpus import thai_words, thai_stopwords
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
import string
import pandas


from clean_doc import clean_alphabet,clean_thaistopwords

def split_word(data):
    #empty this for participants
    words = thai_stopwords()
    thaiwords = clean_thaistopwords()
    en_stop = get_stop_words('en')
    p_stemmer = PorterStemmer()
    
    tokens = word_tokenize(data, engine='newmm')
    #print(tokens)
    
    # remove stop words
    stopped_tokens = [i for i in tokens if not i in words and not i in en_stop and not i in thaiwords]
    #print(stopped_tokens)
    
    # stem words
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    # print(stemmed_tokens)
    
    # remove single alphabet and number
    single_alpha_num_tokens = [i for i in stemmed_tokens if not i in pythainlp.thai_consonants and not i.isnumeric()]
    # print(single_alpha_num_tokens)
    deletelist = [' ', '  ', '   ','none','    ','\n','\x0c']
    tokens = [i for i in single_alpha_num_tokens if not i in deletelist]
    # print("Token :",tokens)
    return tokens