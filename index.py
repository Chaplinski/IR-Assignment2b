#Python 3.5.2
import re
import os
import collections
import time
import math
class index:
    def __init__(self,path):
        self.collection=path
        self.dictionary={}
        self.query_terms=''
        self.query_dict=''
        self.doc_ID_list=[] # list to map docIDs to Filenames, docIDs rn=ange from 0 to n-1 where n is the number of documents.
        start = time.time()
        self.buildIndex()
        end = time.time()
        print("Index built in ", (end - start), " seconds.")
        self.total_number_of_documents = len(self.doc_ID_list)
        self.calculate_idf()
        self.print_dict()
        self.ask_for_query()

    def buildIndex(self):
        #Function to read documents from collection, tokenize and build the index with tokens
        #index should also contain positional information of the terms in the document --- term: [(ID1,[pos1,pos2,..]), (ID2, [pos1,pos2,..]),..]
        #use unique document IDs
        docID=-1
        for filename in os.listdir(self.collection):
            docID=docID+1
            self.doc_ID_list.append(filename)
            #read a document
            lines = open(self.collection + filename).read()
            #tokens = re.split(r'[^A-Za-z]', lines.lower())
            tokens = re.split('\W+',lines.lower());
            self.insert_terms(tokens, docID)
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))

    def insert_terms(self,tokens,docID):
        #add terms to the dict data structure
        #check if term already exists
        pos=-1
        for tok in tokens:
            pos+=1
            if tok == '':
                pass
            elif tok in self.dictionary: # faster
            #elif tok in self.dictionary.keys():
                flag=False
                for index, item in enumerate(self.dictionary[tok]):
                    if item[0] == docID: #add new pos to existing docID entry
                        item[1].append(pos)
                        #self.dictionary[tok][index]=item
                        flag=True
                        break
                if flag == False: #first pos for docID for this tok
                    item=self.dictionary[tok]
                    item.append((docID,[pos]))

            else:   #new docID for this tok
                item=[(docID,[pos])]
                self.dictionary[tok]=item
    def print_dict(self):
    #function to print the terms and posting list in the index
        for key, value in self.dictionary.items():
            print(key, value)
    def get_postinglist(self, term):
        results=[]
        for index,item in enumerate(self.dictionary[term]):
            results.append(item[0])
        return results

    def and_query(self, query_terms):
    #function for identifying relevant docs using the index
        start = time.time()
        #merge operation
        docs = self.and_query_helper(query_terms)
        #print the docs names
        query = ''
        for term in query_terms:
            query += term
            query += ' AND '
        query = query[:-len('AND') - 1]
        print("\nResults for the Query: ", query)
        print("Total Docs retrieved: ", len(docs))
        for item in docs:
            print(self.doc_ID_list[item])
        end = time.time()
        print("Retrieved in ", (end - start), " seconds")
        #self.print_doc_list()

    def and_query_helper(self, query_terms):
        flag = False
        result = []
        matches=[]
        index = 0
        for term in query_terms:
            matches.insert(index,self.get_postinglist(term))
            index += 1
        #return

        # pointers holding the position of each posting list
        # current=[0,0,0,0,...], |current| = query_terms
        current=[0] * len(query_terms)

        max_val = -1 #has the current max doc id
        max_val_cnt = 0 #number of matched terms so far
        index=0
        while flag == False:
            if matches[index][current[index]] == max_val:
                max_val_cnt += 1
                if max_val_cnt >= len(query_terms): # found a term that is in all docs
                    result.append(max_val)
                    current[index] += 1
                    if len(matches[index]) <= current[index]:
                        return result
                    else:
                        max_val = matches[index][current[index]]
                        max_val_cnt = 1
            elif matches[index][current[index]] < max_val:
                flag1 = False
                while flag1 == False:
                    current[index] += 1
                    if len(matches[index]) <= current[index]: # we are done
                        return result
                    if matches[index][current[index]] == max_val:
                        max_val_cnt += 1
                        if max_val_cnt >= len(query_terms): # found a term that is in all docs
                            result.append(max_val)
                            continue
                        else:
                            flag1 = True
                    elif matches[index][current[index]] > max_val:
                        max_val = matches[index][current[index]]
                        max_val_cnt = 1
                        flag1 = True
                    else:
                        continue

            else:
                max_val = matches[index][current[index]]
                max_val_cnt = 1
            index +=1 # look at the next query term
            if index >= len(query_terms):
                index=0 # circle around to the first query term


    def print_doc_list(self):
    # function to print the documents and their document id
        for index, item in enumerate(self.doc_ID_list):
            print('Doc ID: ', index, ' ==> ',item)

    def calculate_idf(self):

        # for each term in dictionary calculate and add the IDF
        for key, value in self.dictionary.items():
            # calculate IDF
            idf = math.log10(self.total_number_of_documents/len(value))
            # print(this_dict)
            # sys.exit()
            # add IDF to list in the first position
            value.insert(0, idf)

    def calculate_tf(self, total_words_in_document, text_id):
        # for each dictionary term
        for key, value in self.dictionary.items():
            # for each document per term in dictionary
            for item in value:
                # if text_id is equal to the text_id of the list item
                if item[0] == text_id:
                    # measure the number of times a word appears in a doc
                    number_of_appearances_in_doc = len(item[1])
                    # divide it by the word count of the entire document
                    tf = number_of_appearances_in_doc
                    # calculate w
                    w = (1 + math.log10(tf))
                    # insert into list
                    item.insert(1, w)

    def exact_query(self, query_terms, k):
        # #function for exact top K retrieval (method 1)
        # #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        #     print('query: ', query_terms)
        #     print('top k: ', k)
        #     print('index: ', self.index)

        # build the dictionaries containing query terms and index terms and their ids and tf-idf
        query_tf_idf_dict = {}
        index_tf_idf_dict = {}
        # for each word in the query
        for word, list in query_terms.items():
            # if that word is not a stop word
            if word not in self.stop_words:
                # get tf-idf of this query term
                query_term_tf_idf = list[0] * list[1]
                query_tf_idf_dict[word] = query_term_tf_idf
                # print('list:', list, 'tf-idf:', query_term_tf_idf)
                # if the word appears in self.index
                if word in self.index:
                    # get idf from the dictionary
                    dictionary_idf = self.index[word][0]
                    # print(word, 'is in the index and its idf value is:', dictionary_idf)
                    for doc_id_list in self.index[word]:
                        # skip the first list item since it is the idf
                        if doc_id_list != self.index[word][0]:
                            # get doc id
                            doc_id = doc_id_list[0]
                            # get word tf
                            word_tf = doc_id_list[1]
                            # get tf-idf of word appearing in this document
                            doc_word_tf_idf = word_tf * dictionary_idf
                            if doc_id in index_tf_idf_dict:
                                # if doc id already exists in index_tf_idf_dict then add to the dictionary that
                                # is its value
                                index_tf_idf_dict[doc_id][word] = doc_word_tf_idf
                                # print('doc id is:', doc_id, 'and tf-idf is:', doc_word_tf_idf)
                            else:
                                # if doc id does not exist in index_tf_idf_dict then add doc id and dictionary
                                # as value. Also add current word and its tf-idf
                                index_tf_idf_dict[doc_id] = {}
                                index_tf_idf_dict[doc_id][word] = doc_word_tf_idf
                                # print('doc id is:', doc_id, 'and tf-idf is:', doc_word_tf_idf)
                                # sys.exit()

        # print('Query tf-idf:', query_tf_idf_dict)
        # print('Index tf-idf', index_tf_idf_dict)

        # for each text id held in index_tf_idf_dict
        for index_key, index_dictionary in index_tf_idf_dict.items():
            numerator = 0
            denominator_index = 0
            denominator_query = 0
            # print('index dictionary: ', index_dictionary)
            # loop through query terms
            for query_key, query_value in query_tf_idf_dict.items():
                # if the query key exists in the index_dictionary
                if query_key in index_dictionary:
                    index_tf_idf = index_dictionary[query_key]
                else:
                    index_tf_idf = 0
                query_tf_idf = query_value
                add_to_numerator = index_tf_idf * query_tf_idf
                numerator += add_to_numerator

                denominator_index += index_tf_idf * index_tf_idf
                denominator_query += query_tf_idf * query_tf_idf
                # print('index tf-idf:', index_tf_idf)
                # print('query tf-idf: ', query_tf_idf)
                # print('Number added:', add_to_numerator)
            # TODO Why is vector so high for document 1?
            # sys.exit()

            # for word, tf_idf in query_tf_idf_dict.items():
            denominator_index_root = math.sqrt(denominator_index)
            denominator_query_root = math.sqrt(denominator_query)
            denominator = denominator_index_root * denominator_query_root
            vector = numerator / denominator
            print('Document', index_key, 'Numerator:', numerator)
            print('Document', index_key, 'Index denominator:', denominator_index_root)
            print('Document', index_key, 'Query denominator:', denominator_query_root)
            print('Document', index_key, 'Denominator:', denominator)
            print('Document', index_key, 'Vector:', vector)

    def convert_string_to_list(self, contents):
        # remove all punctuation and numerals, all text is lowercase
        contents = contents.lower()
        contents = re.sub(r'\d+', '', contents)

        # remove punctuation, replace with a space
        for char in "-:\n":
            contents = contents.replace(char, ' ')

        # remove quotes and apostrophes, replace with empty string
        for char in ".,?!'();$%\"":
            contents = contents.replace(char, '')
        contents = contents.replace('\n', ' ')

        # convert string to list
        contents = contents.split(' ')
        # remove empty strings
        contents = list(filter(None, contents))

        return contents

    # get query and store terms as a list
    def ask_for_query(self):
        query = input("Enter your query: ")
        self.query_terms = self.convert_string_to_list(query)
        self.create_query_dict()
        # create dictionary to keep track of word occurrences in query

    def create_query_dict(self):
        this_dict = {}
        # for each word in query
        for item in self.query_terms:
            # if the word is not in the dictionary add it with a value of 1 occurrence
            if item not in this_dict:
                this_dict.update({item: 1})
            else:
                number_of_occurrences = this_dict.get(item)
                number_of_occurrences += 1
                this_dict.update({item: number_of_occurrences})

        # for each word in the query, calculate the tf-idf
        for key, value in this_dict.items():
            # calculate tf
            number_of_appearances_in_query = value
            # divide it by the word count of the entire query
            tf = number_of_appearances_in_query
            # calculate w
            w = (1 + math.log10(tf))

            idf = ''
            # get idf that is already stored in inverted index
            if key in self.dictionary:
                idf = self.dictionary[key][0]

            # store w and idf as value for word key in this dict
            this_dict[key] = [w, idf]

        self.query_dict = this_dict


# === Testing === #
a=index("collection/")
print(a.query_terms)
print(a.query_dict)
# === End of Testing === #
