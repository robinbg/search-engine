from seindex import SE_INDEX

if __name__ == "__main__":
    index = SE_INDEX()
    index.load_all()
    index.calc_tfidf()
    index.create_all()
    index.close()
