1) Points to notice -> handle cases with of stemming, -> see pdf files
2) read chapter from book
3) index compression technique
4) understand entire flow
5) which stemmer to use 
6) reduce inverted_index file
7) read tf-idf
8) try with different stemmers(Lancaster,Porter,Snowball)

steps -> title processing -> text processing -> for a particular page
do this 30000 page, which account for around 60mb, depends on no of tokens in a page

now sorted, this one file 0.txt, 1.txt and so, on....


now we need to merge this files -> use k-way merge sort using heap, where we read fist line from
each file and then push minimum onto the final_inverted index, 

while creating this inverted index, also create off-set, after certain no of words in (100000)
so that in memory atmost 800 mb of file at a time can be stored,

this selection of file which portion to read is done using binary search on off-set file names

there are 38 temporary offset files, which makes sure only approx 240mb index file is loaded into memory











