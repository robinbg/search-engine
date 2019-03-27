from seindex import SE_INDEX
from collections import defaultdict
import math


class SEARCH_ENGINE(SE_INDEX):

    def __init__(self, print=False):
        SE_INDEX.__init__(self, print)
        self.load_idf()
        self.load_tfidf()


    def lookup_idf(self, term):
        ''' Look up idf value, return 0 if not available '''
        if term in self.idf:
            return self.idf[term]
        return 0.0


    def lookup_tfidf(self, term, docid):
        ''' Look up tfidf value, return [0,0] if not available '''
        if term in self.tfidf:
            if docid in self.tfidf[term]:
                return self.tfidf[term][docid]
        return [0.0, 0.0]


    def dot_product(self, a, b):
        ''' Dot product of two vectors '''
        val = 0.0
        l = len(a)
        if l != len(b):
            return
        for i in range(l):
            val += a[i]*b[i]
        return val


    def get_query_vector(self,query_terms):
        ''' Create a vector for a query '''
        vector = []
        term_count = float(len(query_terms))
        tf = 1 + math.log10(1/term_count)
        for term in query_terms:
            vector.append(tf * self.idf[term])
        return vector


    def cos_sim(self, query_terms):
        ''' Return similarity values for each relevant document '''
        query_vector = self.get_query_vector(query_terms)
        doc_vectors = defaultdict(list)
        weights = defaultdict(float)
        sims = []
        target_docs = set()
        
        for term in query_terms:
            for docid in self.tfidf[term]:
                target_docs.add(docid)

                
        for term in query_terms:
            for docid in target_docs:
                tfidf, w = self.lookup_tfidf(term, docid)
                weights[docid] += w
                doc_vectors[docid].append(tfidf)


        for docid in doc_vectors:
            dp = self.dot_product(query_vector, doc_vectors[docid])
            sims.append([docid, self.docpairs[docid], dp, weights[docid]])

        return sims
    

    def query(self, q):
        ''' Search index for matches, returns list of docids ranked '''
        query_terms = q.lower().split()
        docs = self.cos_sim(query_terms)
        ranked = sorted(docs, key=lambda d: (-d[2], -d[3], d[1]))
        return [d[0] for d in ranked]


        
