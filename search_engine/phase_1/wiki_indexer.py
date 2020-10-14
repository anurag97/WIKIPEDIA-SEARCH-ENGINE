import os
import re
from copy import deepcopy
import xml.sax.handler
from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
from Stemmer import Stemmer
from string import punctuation
from nltk.tokenize import wordpunct_tokenize
import time
import sys
import errno
import heapq
import shutil

stop_words = set(stopwords.words('english'))
stop_words.update(list(char for char in punctuation))
stemmer = Stemmer('english')
text_punc = list(punc for punc in punctuation if punc not in ['{', '}', '=', '[', ']' ])
text_punc.append('\n')

def writing_to_file(Inverted_Index,file_path):
    path_to_write = os.path.join(file_path+'index_file.txt')
    #print("File",str(File_count))
    value = list()
    file_pointer = open(path_to_write, 'w+')
    for term in sorted(Inverted_Index):
        temp = term + ' '
        temp = temp + '|'.join(item for item in Inverted_Index[term])
        value.append(temp)
    if len(value):
            file_pointer.write('\n'.join(value).encode('utf-8').decode())
    file_pointer.close()

class CreateIndex(xml.sax.ContentHandler):
    def __init__(self):
        self.istitle = False
        self.istext = False
        self.isfirstid = False
        self.isid = False
        self.title = ""
        self.text = ""
        self.docid = ""
        self.inverted_index = dict()
        self.page_count = 0
        self.file_count = 0
        self.first = 0
        self.token_casefolding = 0
        
    def title_processing(self,title_string):
        title_frequency = dict()
        title_string = re.sub('\\b[-\.]\\b', '', title_string)
        title_string = re.sub('[^A-Za-z0-9\{\}\[\]\=]+',' ', title_string)
        for each_word in wordpunct_tokenize(title_string):
            # each_word = each_word.lower()
            self.token_casefolding = self.token_casefolding + 1
            if each_word.lower() not in stop_words:
                each_word = stemmer.stemWord(each_word.lower())
                if each_word not in title_frequency:
                    title_frequency[each_word] = 0  
                title_frequency[each_word]+= 1

        return title_frequency
    
    def text_processing(self,text_string):
        # t = title, b = body, i = infobox, c = category, l = link, r = reference

        text_string = re.sub('[^A-Za-z0-9\{\}\[\]\=]+',' ', text_string)
        text_frequency = dict()

        regex_category = re.compile(r'\[\[Category(.*?)\]\]')
        table = str.maketrans(dict.fromkeys('\{\}\=\[\]'))

        new_text = regex_category.split(text_string)
        
        if len(new_text) > 1:
            for text in new_text[1:]:
                text = text.translate(table)
                for word in wordpunct_tokenize(text):
                    # word = word.lower()
                    if word.lower() not in text_frequency:
                        text_frequency[word.lower()] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
                    text_frequency[word.lower()]['c'] += 1

            text_string = new_text[0]

        new_text = text_string.split('==External links==')
        if len(new_text) > 1:
            new_text[1] = new_text[1].translate(table)

            for word in wordpunct_tokenize(new_text[1]):
                # word = word.lower()
                if word.lower() not in text_frequency:
                    text_frequency[word.lower()] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
                text_frequency[word.lower()]['l'] += 1

            text_string = new_text[0]

        new_text = text_string.split("{{Infobox")

        braces_count = 1
        default_tag_type = 'i'

        if len(new_text) > 1:
            new_text[0] = new_text[0].translate(table)

            for word in wordpunct_tokenize(new_text[0]):
                # word = word.lower()
                if word.lower() not in text_frequency:
                    text_frequency[word.lower()] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
                text_frequency[word.lower()]['b'] += 1



            for word in re.split(r"[^A-Za-z0-9]+",new_text[1]):
                # word = word.lower()
                if "}}" in word.lower():
                    braces_count -= 1
                if "{{" in word.lower():
                    braces_count += 1
                    continue
                if braces_count == 0:
                    default_tag_type = 'b'

                word = word.lower().translate(table)

                if word not in text_frequency:
                    text_frequency[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
                text_frequency[word][default_tag_type] += 1


        else:
            text_string = text_string.translate(table)
            for word in wordpunct_tokenize(text_string):
                word = word.lower()
                if word.lower() not in text_frequency:
                    text_frequency[word.lower()] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
                text_frequency[word.lower()]['b'] += 1


        duplicate_copy = dict()
        for term in text_frequency:
            self.token_casefolding = self.token_casefolding + 1
            stemmed_term = stemmer.stemWord(term)
            if stemmed_term not in duplicate_copy:
                duplicate_copy[stemmed_term] = text_frequency[term]
            else:
                for key in duplicate_copy[stemmed_term]:
                    duplicate_copy[stemmed_term][key] += text_frequency[term][key]

        text_frequency = dict()
        for term in duplicate_copy:
             if term not in stop_words or term != '':
                text_frequency[term] = duplicate_copy[term]

        return text_frequency
    
    def preprocessing(self,title,text):

        page_count = self.page_count
        title_frequency = self.title_processing(title)
        text_frequency = self.text_processing(text)
        file_pointer = open("2019201007/DocID_Title_mapping.txt",'a+')
        if self.first == 1:
            file_pointer.write('\n')

        if self.first == 0:
            self.first = 1

        value = str(page_count) + ' '+ title
        value = value.encode('utf-8').decode()

        for word_title in title_frequency:
            if word_title in text_frequency:
                text_frequency[word_title]['t'] += title_frequency[word_title]
            else:
                text_frequency[word_title] = dict(d=page_count,t=title_frequency[word_title],b=0,i=0,c=0,l=0,r=0)

        file_pointer.write(value)
        file_pointer.close()

        for term in text_frequency:
            if len(term) < 3 or term.startswith('0'):
                continue
            text_frequency[term]['d'] = str(page_count)
            if term not in self.inverted_index:
                self.inverted_index[term] = list()
            self.inverted_index[term].append(''.join(tag + str(text_frequency[term][tag]) for tag in text_frequency[term] if text_frequency[term][tag] != 0))
        
    def startElement(self,name,attribute):
        if name == "title":
            self.istitle = True
            self.title = ""
        elif name == "text":
            self.istext = True
            self.text = ""
        elif name == "page":
            self.isfirstid = True
            self.docid = ""
        elif name == "id" and self.isfirstid:
            self.isid = True
            self.isfirstid = False
            
    def endElement(self,name):
        if name == "title":
            self.istitle = False
        elif name == "text":
            self.istext = False
        elif name == "id":
            self.isid = False
#             self.isfirstid = False ## Changeable Areas
        elif name == "page":
            self.page_count = self.page_count + 1
            text = deepcopy(self.text)
            title = deepcopy(self.title)
            id_page = deepcopy(self.docid)
            self.preprocessing(title,text)
        
    def characters(self,content):
        if self.istitle:
            self.title = self.title + content
        elif self.istext:
            self.text = self.text + content
        elif self.isid:
            self.docid = self.docid + content

if __name__ == "__main__":
    
    start = time.time()
    xml_parser = xml.sax.make_parser()
    Indexer = CreateIndex()
    xml_parser.setContentHandler(Indexer)
    xml_parser.parse(sys.argv[1])
    writing_to_file(Indexer.inverted_index, sys.argv[2])
    end = time.time()
    
    # create_offset_files()
    print("Time Taken to build an Inverted Index is : " + str(end - start) + " seconds")
    # count_token_in_index_file()
    # build_inverted_index_stat()
