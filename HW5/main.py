import os
import math
import re
from pathlib import Path

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

# nltk.download("stopwords")

RUS_ENG_STOPWORDS = stopwords.words("russian") + stopwords.words("english")
DOCS_PATH = "./tfidf_lemmas"
INDEX_FILE = "./index.txt"


def preprocess_text(text):
    tokenizer = RegexpTokenizer(r"[А-Яа-яЁё]+")
    tokens = tokenizer.tokenize(text.lower())
    return [t for t in tokens if t not in RUS_ENG_STOPWORDS]


def lemmatize_words(words):
    analyzer = MorphAnalyzer()
    return [analyzer.parse(word)[0].normal_form for word in words if re.match(r"[А-Яа-яЁё]", word)]


def compute_norm(vector):
    return math.sqrt(sum(x * x for x in vector))


def load_index():
    with open(INDEX_FILE, encoding="utf-8") as f:
        return {int(line.split()[0]): line.strip().split()[1] for line in f}


def load_documents_vectors():
    result = []
    files = sorted(Path(DOCS_PATH).glob("tfidf_lemmas_*.txt"))
    for file in files:
        with open(file, encoding="utf-8") as f:
            vec = {line.split()[0]: float(line.split()[1]) for line in f}
            result.append(vec)
    return result


def tf_idf_score(term, term_list, total_docs, docs_with_term):
    tf = term_list.count(term) / len(term_list)
    idf = math.log(total_docs / docs_with_term) if docs_with_term else 0
    return round(tf * idf, 6)


def similarity_score(vec1, vec2):
    numerator = sum(a * b for a, b in zip(vec1, vec2))
    if numerator == 0:
        return 0
    return numerator / (compute_norm(vec1) * compute_norm(vec2))


def find_similar_documents(user_query):
    index_data = load_index()
    document_vectors = load_documents_vectors()

    tokens = preprocess_text(user_query)
    lemmas = lemmatize_words(tokens)

    if not lemmas:
        return []

    total_docs = len(document_vectors)
    query_vec = []

    for lemma in lemmas:
        doc_count = sum(1 for doc in document_vectors if lemma in doc)
        query_vec.append(tf_idf_score(lemma, lemmas, total_docs, doc_count))

    scores = {}
    for i, doc_vec in enumerate(document_vectors):
        doc_vector = [doc_vec.get(lemma, 0.0) for lemma in lemmas]
        scores[i] = similarity_score(query_vec, doc_vector)

    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [
        {"doc_id": doc_id, "link": index_data.get(doc_id, "unknown"), "cosine_sim": sim}
        for doc_id, sim in sorted_results if sim >= 0.05
    ]


if __name__ == "__main__":
    q = input("Введите поисковый запрос: ")
    output = find_similar_documents(q)
    for item in output:
        print(f"Документ {item['doc_id']} | Ссылка: {item['link']} | Сходство: {item['cosine_sim']:.2f}")
