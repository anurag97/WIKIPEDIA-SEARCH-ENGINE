import os
import re
from copy import deepcopy
import xml.sax.handler
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
# from nltk.stem.lancaster import LancasterStemmer

# from Stemmer import Stemmer
from string import punctuation
from nltk.tokenize import wordpunct_tokenize
import time
import sys
import errno
import heapq
import shutil


stop_words = set(stopwords.words('english'))

stop_words.update(list(char for char in punctuation))

# stemmer = Stemmer('english')
stemmer = SnowballStemmer("english")

text_punc = list(punc for punc in punctuation if punc not in [
                 '{', '}', '=', '[', ']'])

text_punc.append('\n')


# words_left = ['{', '}', '=', '[', ']' ]

def writing_to_file(Inverted_Index, File_count, file_path):
    path_to_write = os.path.join(file_path, str(File_count) + '.txt')
    # print("File",str(File_count))
    value = list()
    file_pointer = open(path_to_write, 'w+')
    for term in sorted(Inverted_Index):
        temp = term + ' '
        temp = temp + '|'.join(item for item in Inverted_Index[term])
        value.append(temp)
    if len(value):
        file_pointer.write('\n'.join(value).encode('utf-8').decode())

    file_pointer.close()


def compress_docid(word_list):
    inverted_index = list()
    posting_list = word_list.split('|')
    inverted_index.append(posting_list[0])
    post = posting_list[0].split('d')
    k = post[1]
    new_str = ""
    z = 0
    y = 0
    x = 0
    for i in range(1, len(posting_list)):
        # print(posting_list[i])
        posts = posting_list[i].split('d')
        try:
            y = int(str(posts[1].strip()))
            x = int(k)
            doc_id = str(y-x)
            posting_instance = posts[0] + 'd' + doc_id
            inverted_index.append(posting_instance)
            k = posts[1]
        except Exception as e:
            dummy = 0
        
    if(len(inverted_index)>1):
        new_str = '|'.join(item for item in inverted_index)
    else:
        new_str = inverted_index[0]
    return new_str


def main_file_write(words, inverted_index, index_file_path, offset_file_path, offset):
    items_to_write = list()
    offset_list = list()
    try:
        file_pointer = open(index_file_path, 'a+')
        file_pointer1 = open(offset_file_path, 'a+')
        for word in words:
            offset_term = word + ' ' + str(offset)
            word_text = word + ' '
            x = '|'.join(list(item for item in inverted_index[word]))
            new_x = compress_docid(x)
            # print(new_x)
            # new_x = '|'.join(list(item for item in inverted_index[word]))
            word_text = word_text + new_x
            # print(word_text)

            offset_list.append(offset_term)
            items_to_write.append(word_text)
            offset = offset + len(word_text) + 1

        if len(offset_list):
            file_pointer1.write(
                '\n'.join(offset_list).encode('utf-8').decode())
            file_pointer1.write('\n')

        if len(items_to_write):
            file_pointer.write(
                '\n'.join(items_to_write).encode('utf-8').decode())
            file_pointer.write('\n')

        file_pointer.close()
        file_pointer1.close()
    except Exception as e:
        print("Error while opening the Index File. Exiting..")
    finally:
        file_pointer.close()
        file_pointer1.close()

    return offset


def Merge_files(file_count, index_path):

    if not os.path.exists(index_path):
        try:
            os.makedirs(index_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise

    file_pointer = list()
    end_of_file = list()
    list_of_words = list()
    heap = list()

    # read all files in intermediate directory, and read only first lines from those files
    # and insert those into heap
    #
    for index in range(file_count):
        path_of_file = os.path.join('intermediate', str(index) + '.txt')
        file_pointer.append(open(path_of_file, 'r'))
        list_of_words.append(file_pointer[index].readline().split(' ', 1))
        if list_of_words[index][0] not in heap:
            heapq.heappush(heap, list_of_words[index][0])
        end_of_file.append(0)

    index_file_path = os.path.join(index_path, 'index_file' + '.txt')
    offset_file_path = "offset_file.txt"
    try:
        os.remove(index_file_path)
        os.remove(offset_file_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

    offset = 0
    flag = 0
    words = list()
    inverted_index = dict()
    while heap:
        top_most_word = heapq.heappop(heap)
        if top_most_word == "":
            continue
        words.append(top_most_word)
        if top_most_word not in inverted_index:
            inverted_index[top_most_word] = list()

        for index in range(file_count):

            if end_of_file[index] == 1:
                continue

            if list_of_words[index][0] == top_most_word:
                inverted_index[top_most_word].append(
                    list_of_words[index][1].strip())
                list_of_words[index] = file_pointer[index].readline().split(
                    ' ', 1)

                if list_of_words[index][0] == "":
                    file_pointer[index].close()
                    end_of_file[index] = 1
                    continue

                if list_of_words[index][0] not in heap:
                    heapq.heappush(heap, list_of_words[index][0])

        if len(words) % 100000 == 0:
            offset = main_file_write(
                words, inverted_index, index_file_path, offset_file_path, offset)
            flag = 1
            inverted_index = dict()
            words = list()

    if len(words):
        offset = main_file_write(
            words, inverted_index, index_file_path, offset_file_path, offset)


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

    def title_processing(self, title_string):

        title_frequency = dict()
        title_string = re.sub('\\b[-\.]\\b', '', title_string)
        title_string = re.sub('[^A-Za-z0-9\{\}\[\]\=]+', ' ', title_string)
        for each_word in wordpunct_tokenize(title_string):
            # each_word = each_word.lower()
            if each_word.lower() not in stop_words:
                # each_word = stemmer.stemWord(each_word.lower())
                each_word = stemmer.stem(each_word.lower())
                if each_word not in title_frequency:
                    title_frequency[each_word] = 0
                title_frequency[each_word] += 1

        return title_frequency

    def text_processing(self, text_string):

        text_string = re.sub('[^A-Za-z0-9\{\}\[\]\=]+', ' ', text_string)
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
                        text_frequency[word.lower()] = dict(
                            t=0, b=0, i=0, c=0, l=0, r=0)
                    text_frequency[word.lower()]['c'] += 1

            text_string = new_text[0]

        new_text = text_string.split('==External links==')
        if len(new_text) > 1:
            new_text[1] = new_text[1].translate(table)

            for word in wordpunct_tokenize(new_text[1]):
                # word = word.lower()
                if word.lower() not in text_frequency:
                    text_frequency[word.lower()] = dict(
                        t=0, b=0, i=0, c=0, l=0, r=0)
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
                    text_frequency[word.lower()] = dict(
                        t=0, b=0, i=0, c=0, l=0, r=0)
                text_frequency[word.lower()]['b'] += 1

            for word in re.split(r"[^A-Za-z0-9]+", new_text[1]):
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
                    text_frequency[word] = dict(t=0, b=0, i=0, c=0, l=0, r=0)
                text_frequency[word][default_tag_type] += 1

        else:
            text_string = text_string.translate(table)
            for word in wordpunct_tokenize(text_string):
                word = word.lower()
                if word.lower() not in text_frequency:
                    text_frequency[word.lower()] = dict(
                        t=0, b=0, i=0, c=0, l=0, r=0)
                text_frequency[word.lower()]['b'] += 1

        duplicate_copy = dict()
        for term in text_frequency:
            # stemmed_term = stemmer.stemWord(term)
            stemmed_term = stemmer.stem(term)
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

    def preprocessing(self, title, text):

        page_count = self.page_count
        title_frequency = self.title_processing(title)
        text_frequency = self.text_processing(text)
        file_pointer = open("DocID_Title_mapping.txt", 'a+')
        if self.first == 1:
            file_pointer.write('\n')

        if self.first == 0:
            self.first = 1

        value = str(page_count) + ' ' + title
        value = value.encode('utf-8').decode()

        for word_title in title_frequency:
            if word_title in text_frequency:
                text_frequency[word_title]['t'] += title_frequency[word_title]
            else:
                text_frequency[word_title] = dict(
                    d=page_count, t=title_frequency[word_title], b=0, i=0, c=0, l=0, r=0)

        file_pointer.write(value)
        file_pointer.close()

        for term in text_frequency:
            if len(term) < 3 or term.startswith('0'):
                continue
            text_frequency[term]['d'] = str(page_count)
            if term not in self.inverted_index:
                self.inverted_index[term] = list()
            self.inverted_index[term].append(''.join(tag + str(text_frequency[term][tag])
                                                     for tag in text_frequency[term] if text_frequency[term][tag] != 0))

        if self.page_count % 30000 == 0:
            writing_to_file(self.inverted_index,
                            self.file_count, 'intermediate')
            self.file_count = self.file_count + 1
            self.inverted_index = dict()

    def startElement(self, name, attribute):

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
            self.id = True
            self.isfirstid = False

    def endElement(self, name):

        if name == "title":
            self.istitle = False
        elif name == "text":
            self.istext = False
        elif name == "id":
            self.isid = False
            # self.isfirstid = False ## Changeable Areas
        elif name == "page":
            self.page_count = self.page_count + 1
            text = deepcopy(self.text)
            title = deepcopy(self.title)
            self.preprocessing(title, text)

    def characters(self, content):

        if self.istitle:
            self.title = self.title + content
        elif self.istext:
            self.text = self.text + content
        elif self.isid:
            self.docid = self.docid + content


def create_offset_files():
    if not os.path.exists('temp_offsets'):
        os.mkdir('temp_offsets')
    else:
        shutil.rmtree('temp_offsets')
        os.mkdir('temp_offsets')

    file_ptr = None
    with open('offset_file.txt') as offset_file:
        for lineno, line in enumerate(offset_file):
            if lineno % 1000000 == 0:
                if file_ptr:
                    file_ptr = None
                value = line.strip().split(' ')[0]
                file_path = os.path.join('temp_offsets', value + '.txt')
                file_ptr = open(file_path, "w")
            file_ptr.write(line)
        if file_ptr:
            file_ptr.close()


if __name__ == "__main__":

    sys.setrecursionlimit(1500)

    start = time.time()
    if not os.path.exists('intermediate'):
        try:
            os.makedirs('intermediate')
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise

    try:
        os.remove('DocID_Title_mapping.txt')
    except OSError as e:
        pass

    xml_parser = xml.sax.make_parser()

    Indexer = CreateIndex()
    xml_parser.setContentHandler(Indexer)

    for xml_file in os.listdir(sys.argv[1]):
    	xml_parser.parse(os.path.join(sys.argv[1],xml_file))

    # xml_parser.parse(sys.argv[1])

    if Indexer.page_count % 30000 > 0:
        writing_to_file(Indexer.inverted_index,
                        Indexer.file_count, 'intermediate')
        Indexer.file_count += 1

    Merge_files(Indexer.file_count, sys.argv[2])
    end = time.time()
    print("Time Taken to build an Inverted Index is : " +
          str(end - start) + " seconds")
    shutil.rmtree('intermediate')
    create_offset_files()
    os.remove("offset_file.txt")
