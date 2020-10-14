
import os
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
# from Stemmer import Stemmer
import time
import sys
import math
import operator

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def query_processing(query):
	global stop_words
	global stemmer
	queries = dict()
	# field_reg = re.compile(r'[a-z]+:[A-Za-z0-9]+[ ]?')
	field_list = ['title:', 'body:','category:','infobox:','ref:']
	query = query.lower()
	field_reg = re.finditer('(title:|infobox:|body:|category:|ref:)([\w+\s+]+)(?=(title:|infobox:|body:|category:|ref:|$))',query)
	if any(1 for field in field_list if field in query):
		#query_regex = field_reg.findall(query)
		# print("query_regex :", query_regex)
		for elem in field_reg:
			term = elem.group(0).split(":")
			#print(term)
			try:
				term_list = list(stemmer.stem(word.lower()) for word in term[1].split() if word not in stop_words)
				for t in term_list:
					queries[term[0]].append(t)
			except KeyError:
				queries[term[0]] = list(stemmer.stem(word.lower()) for word in term[1].split() if word not in stop_words)
	else:
		words = query.strip().split(' ')
		try:
			term_list = list(stemmer.stem(word.lower()) for word in words if word not in stop_words)
			for t in term_list:
				queries['all'].append(t)
		except KeyError:
			queries['all'] = list(stemmer.stem(word.lower()) for word in words if word not in stop_words)

	return queries

def searching(query,index_path):

	print("Loading index file.........")

	index_path = os.path.join(index_path, 'index_file.txt')
	index_file_ptr = open(index_path,'r')
	
	result = dict()

	posting_lists =  index_file_ptr.readlines()
	queries_index = dict()
	for lines in posting_lists:
		line_split = lines.split(' ')
		queries_index[line_split[0]] = (line_split[1])

	print("Loaded.............")

	for key in query:
		if key in ['all']:
			for word in query['all']:
				print(word)
				print(queries_index[word])

		else:
			for word in query[key]:
				print(word)
				print(queries_index[word])

def main():

	processed_queries = query_processing(sys.argv[2])
	#print("Modified Query : ", processed_queries)
	posting_list = searching(processed_queries,sys.argv[1])

if __name__ == "__main__":
	main()