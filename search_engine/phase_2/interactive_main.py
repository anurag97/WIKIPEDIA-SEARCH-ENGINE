
# def main():
# 	# query_list = read_query_file(sys.argv[2])
# 	print("Loading Titles-Document ID Mappings....")
# 	titles = get_titles()
# 	number_document = len(titles)
# 	print("Loaded...")
# 	#output_path = sys.argv[2]
# 	#file_ptr_output = open(output_path, 'w+')
# 	file_pointer = open('queries.txt')
# 	while True:
# 		#print("Original Query : ", query)
# 		print()
# 		query = input("Enter the Query (Press Q to Quit) : ")
# 		if query == "Q":
# 			break
# 		start = time.time()
# 		processed_queries = query_processing(query)
# 		#print("Modified Query : ", processed_queries)
# 		result = searching(processed_queries,sys.argv[1],number_document)
# 		#print(result)
# 		print("Results : ")
# 		if len(result) > 0:
# 			if len(result) > 10:
# 				result = result[:10]
# 			for r in result:
# 				#print("Title of the Document : ", titles[r[0]])
# 				print(titles[r[0]])
# 				#file_ptr_output.write('\n')
# 		#file_ptr_output.write('\n')
# 		#file_ptr_output.write('\n')
# 		end = time.time()
# 		print("Response Time for the Query " + query + " is " +  str(end - start) + " seconds")

# 	#file_ptr_output.close()
# 	print()
# 		#print("***" * 30)
