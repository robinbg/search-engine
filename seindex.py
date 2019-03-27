import lxml
import json
import nltk
import re
nltk.download('stopwords')
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import pickle
import math



class SE_INDEX:

    def __init__(self, print=False):
        self.print = print  
        self.limit_counter = 0
        self.main_directory = "WEBPAGES_RAW/"
        self.bookkeeping = open(self.main_directory + "bookkeeping.json")
        self.docpairs = json.load(self.bookkeeping)
        self.stopwords = set(stopwords.words("english"))
        self.postings = dict()
        self.doc_counts = dict()
        self.idf = dict()
        self.tfidf = dict()


    def tokenize(self, text):
        ''' Strip all but english alphanumerics from text '''
        token_list = []
        token_regex = "[a-z0-9]+"
        for token in re.findall(token_regex, text.lower()):
            if not token.isdigit() and not token in self.stopwords and len(token) > 1:
                token_list.append(token)
        return token_list


    def update_posting(self, tokens, page, freq=1, strong=0, section=None):
        ''' Update a posting in the postings list '''
        for token in tokens:
            if token in self.postings:
                if page in self.postings[token]:
                    self.postings[token][page][0] += freq
                    if strong == 1:
                        self.postings[token][page][1] = strong
                    if section != None:
                        self.postings[token][page][2] = section
                else:
                    self.postings[token][page] = [freq, strong, section]
            else:
                self.postings[token] = {page: [freq, strong, section]}


    def check_bold(self, page, soup):
        ''' Check if a term is bold '''
        bold = soup.find_all('b')
        for tag in bold:
            tokenized = self.tokenize(tag.get_text())
            self.update_posting(tokenized, page, 1, 1, None)


    def check_section(self, page, soup, section):
        ''' Check what section a term falls in title, header, body '''
        section_tags = soup.find_all(section)
        for tag in section_tags:
            tokenized = self.tokenize(tag.get_text())
            self.update_posting(tokenized, page, 1, 0, section)
        

    def parse_docs(self, limit):
        ''' Parse documents '''
        limit_counter = 0
        for page in self.docpairs:
            if limit_counter >= limit: break
            with open(self.main_directory + page, encoding="utf8") as current_page:
                soupPage = BeautifulSoup(current_page, "lxml")
            self.check_section(page, soupPage, "title")
            self.check_section(page, soupPage, "header")
            self.check_section(page, soupPage, "body")
            self.check_bold(page, soupPage)
            tokens = self.tokenize(soupPage.get_text())
            self.doc_counts[page] = len(tokens)
            self.update_posting(tokens, page)
            current_page.close()
            limit_counter += 1
            if self.print:
                print("Parsed " + page)
        self.get_stats()


    def calc_term_weight(self, strong, pos):
        ''' Calculate weight offset '''
        w = 0
        if strong == 1:         w += 1
        if pos == "title":      w += 3
        elif pos == "header":   w += 2
        return w


    def calc_tfidf(self):
        ''' Calculate tf*idf value and weight of each term, doc '''
        # tf = 1 + log10(# of times term in doc / total # of terms in doc)
        # idf = log10(total # of documents / # of documents with term)
        for term in self.postings:
            docs_with_term = len(self.postings[term])
            idf = math.log10(self.doc_count / docs_with_term)
            self.idf[term] = idf
            self.tfidf[term] = dict()
            for docid in self.postings[term]:
                freq, strong, pos = self.postings[term][docid]
                terms_in_doc = self.doc_counts[docid]
                tf = 1 + math.log10(float(freq) / terms_in_doc)
                tfidf = tf * idf
                self.tfidf[term][docid] = [tfidf, self.calc_term_weight(strong, pos)]
            if self.print:
                print("Calculated (tf*idf , weight) values for {}".format(term))


    def get_stats(self):
        self.doc_count = float(len(self.docpairs))
        self.term_count = len(self.postings)


    def create_post_list(self):
        ''' Store postings list in pickle file '''
        post_list_out = open("INDEX/post_list.pickle", "wb")
        pickle.dump(self.postings, post_list_out)
        print("Stored postings in post_list.pickle.")


    def create_doc_list(self):
        ''' Store document list in pickle file '''
        doc_list_out = open("INDEX/doc_list.pickle", "wb")
        pickle.dump(self.docpairs, doc_list_out)
        print("Stored document list in doc_list.pickle.")
        doc_list_out.close()


    def create_doc_counts(self):
        ''' Store document term counts in pickle file '''
        doc_counts_out = open("INDEX/doc_counts.pickle", "wb")
        pickle.dump(self.doc_counts, doc_counts_out)
        print("Stored term counts in doc_counts.pickle")
        doc_counts_out.close()


    def create_idf(self):
        ''' Store idf in pickle file '''
        idf_out = open("INDEX/idf.pickle", "wb")
        pickle.dump(self.idf, idf_out)
        print("Stored idf values in idf.pickle")
        idf_out.close()
        

    def create_tfidf(self):
        ''' Store tfidf in pickle file '''
        tfidf_out = open("INDEX/tfidf.pickle", "wb")
        pickle.dump(self.tfidf, tfidf_out)
        print("Stored tf*idf values tfidf.pickle")
        tfidf_out.close()


    def create_all(self):
        ''' Store all files '''
        self.create_post_list()
        self.create_doc_list()
        self.create_doc_counts()
        self.create_idf()
        self.create_tfidf()


    def generate(self):
        ''' Generate all index files '''
        self.parse_docs()
        self.calc_tfidf()
        self.create_all()


    def load_post_list(self):
        ''' Read postings list in pickle file '''
        try:
            post_list_in = open("INDEX/post_list.pickle", "rb")
            self.postings = pickle.load(post_list_in)
            print("Loaded postings.")
            post_list_in.close()
        except EOFError:
            print("Could not load postings list, file was empty.")
        except FileNotFoundError:
            print("Could not load postings list, file not found.")            


    def load_doc_list(self):
        ''' Read document list in pickle file '''
        try:
            doc_list_in = open("INDEX/doc_list.pickle", "rb")
            self.docpairs = pickle.load(doc_list_in)
            print("Loaded document list.")
            doc_list_in.close()
        except EOFError:
            print("Could not load document list, file was empty.")
        except FileNotFoundError:
            print("Could not load document list, file not found.")            


    def load_doc_counts(self):
        ''' Read document term counts in pickle file '''
        try:
            doc_counts_in = open("INDEX/doc_counts.pickle", "rb")
            self.doc_counts = pickle.load(doc_counts_in)
            print("Loaded term counts.")
            doc_counts_in.close()
        except EOFError:
            print("Could not load term counts, file was empty.")
        except FileNotFoundError:
            print("Could not load term counts, file not found.")


    def load_idf(self):
        ''' read idf in pickle file '''
        try:
            idf_in = open("INDEX/idf.pickle", "rb")
            self.idf = pickle.load(idf_in)
            print("Loaded idf values.")
            idf_in.close()
        except EOFError:
            print("Could not load idf values, file was empty.")
        except FileNotFoundError:
            print("Could not load idf values, file not found.")
        

    def load_tfidf(self):
        ''' Read tfidf in pickle file '''
        try:
            tfidf_in = open("INDEX/tfidf.pickle", "rb")
            self.tfidf = pickle.load(tfidf_in)
            print("Loaded tf*idf values.")
            tfidf_in.close()
        except EOFError:
            print("Could not load tf*idf values, file was empty.")
        except FileNotFoundError:
            print("Could not load tf*idf values, file not found.")
            

    def load_all(self):
        ''' Load all files '''
        self.load_post_list()
        self.load_doc_list()
        self.load_doc_counts()
        self.load_idf()
        self.load_tfidf()
        self.get_stats()


    def close(self):
        ''' Close files '''
        self.bookkeeping.close()


