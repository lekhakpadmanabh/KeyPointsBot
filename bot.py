import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import pairwise_kernels
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from goose import Goose
from scipy import sparse
import sqlite3 as lite
from time import sleep 
import praw

conn = lite.connect("bot.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS botlog(id INTEGER PRIMARY KEY, 
                  reddit_id TEXT unique, toi_url TEXT,
                  imgur_url TEXT)
               ''')
def add_record(reddit_id, toi_url, imgur_url):
    """Insert id and urls into db"""

    try:
        cursor.execute("INSERT INTO botlog (reddit_id,toi_url,imgur_url) \
                        VALUES (?,?,?)", (reddit_id,toi_url,imgur_url));
        conn.commit()
    except lite.IntegrityError:
        print "Reddit id {} already exists".format(reddit_id)

def check_record(reddit_id):
    """check if given id has been processed previously"""

    cursor.execute("SELECT reddit_id from botlog where reddit_id=?",
                   (reddit_id,))
    return cursor.fetchone()

def format_keypoints(key_points):
    if not len(key_points) == 4:
        print key_points
        return "FAILURE!!!!! Make sure it doesn't post"
    return u">* {0}\n>* {1}\n>* {2}\n>* {3}\n".format(*[p[2].rstrip() for p in key_points])


try:
    import configparser as cfg
except ImportError:
    import ConfigParser as cfg

#get configs
conf = cfg.ConfigParser()
conf.read("config.ini")
USERNAME = conf.get('REDDIT','USERNAME')
PASSWORD = conf.get('REDDIT','PASSWORD')
USERAGENT = conf.get('GENERAL','USERAGENT')
SUBREDDITS = ("worldnews",)
r = praw.Reddit(user_agent=USERAGENT)
r.login(USERNAME, PASSWORD)

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
stops = stopwords.words('english')
lemtz = WordNetLemmatizer()

def goose_extractor(url):
    """get article contents"""

    article = Goose().extract(url=url)
    return article.title, article.meta_description,\
                              article.cleaned_text

def sentence_tokens(text):
    """sentence tokenize"""

    return sent_detector.tokenize(text)

def preprocess(sentences):
    """lowercase, stopword removal, lemmatization"""

    return [lemtz.lemmatize(s.lower()) for s in sentences if s not in stops]

def vectorize_normalize(sentences):
    """vectorize and return tf-idf matrix"""

    bag = CountVectorizer(min_df=1,ngram_range=(1,2)).fit_transform(sentences)
    return TfidfTransformer().fit_transform(bag)

def textrank(matrix):
    """return textrank vector"""

    nx_graph = nx.from_scipy_sparse_matrix(sparse.csr_matrix(matrix))
    return nx.pagerank(nx_graph)

def summarizer(url, num_sentences=4):
    """return top-[num_sentences] 'summary'"""

    title, hsumm, full_text = goose_extractor(url)
    sentences = sentence_tokens(full_text)
    _sentences = preprocess(sentences)
    norm = vectorize_normalize(_sentences)
    similarity_matrix = pairwise_kernels(norm, metric='cosine')
    scores = textrank(similarity_matrix)
    scored_sentences = []
    for i, s in enumerate(sentences):
        scored_sentences.append((scores[i],i,s))
    top_scorers = sorted(scored_sentences, key=lambda tup: tup[0], 
                         reverse=True)[:num_sentences]
    return hsumm, sorted(top_scorers, key=lambda tup: tup[1])

COMMENT =\
u"""
**Summary**: {summary}\n
**Key Points**\n ---
{keypoints}\n --- 
^I'm ^a ^bot \
^| [^Message ^Creator](http://www.reddit.com/message/compose/?to=padmanabh) ^| \
[^Code](https://github.com/lekhakpadmanabh/ToIBot)
"""
