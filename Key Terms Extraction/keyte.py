from string import punctuation
from lxml import etree
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer

text = 'news.xml'
corpus = etree.parse(text).getroot().find("corpus")
exclude = list(punctuation) + stopwords.words('english')
lem = WordNetLemmatizer()
vec = TfidfVectorizer()
headlines = []
documents = []
for news in corpus:
    headlines.append(news.find("value[@name='head']").text)
    tokens = word_tokenize(news.find("value[@name='text']").text.lower())
    lemmas = [lem.lemmatize(x) for x in tokens]
    tokens_after_ex = [x for x in lemmas if x not in exclude]
    word_pos = [pos_tag([word]) for word in tokens_after_ex]
    nouns = [word[0][0] for word in word_pos if word[0][1] == "NN"]
    documents.append(" ".join(nouns))

tfidf_array = vec.fit_transform(documents).toarray()
terms = vec.get_feature_names_out()

for i, headline in enumerate(headlines):
    freq_dict_sorted = dict(
        sorted(zip(terms, tfidf_array[i]), key=lambda x: (x[1], x[0]), reverse=True)
    )
    print(f"{headline}:\n{' '.join(list(freq_dict_sorted)[:5])}\n")
