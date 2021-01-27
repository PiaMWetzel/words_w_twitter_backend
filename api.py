from flask import Flask, request, render_template, send_file
import seaborn as sns
import matplotlib.pyplot as plt
import tweepy
import nltk
import pandas as pd
import numpy as np
import base64
import io

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
snowball = nltk.stem.SnowballStemmer('english', ignore_stopwords=True)


def get_words(timeline, username):
    print(len(timeline))
    tweets = [t.text for t in timeline if t.retweeted == False]
    tweets2 = [tweet for tweet in tweets if not tweet.startswith("RT ")]
    tweets = tweets2

    tokens = [t for tweet in tweets for t in tweet.split()]
    print(tokens)
    words = [token.lower() for token in tokens if token.isalpha()]

    links = ('www', 'http', 'https')
    stops = set(stopwords.words('english'))
    stops = stops.union(links)
    stop = [stem for stem in words if stem not in stops]
    stems = [snowball.stem(s) for s in stop]

    df = pd.DataFrame(stems)
    df = df[0].value_counts()
    print(df[0])

    plt.rcdefaults()

    df = df[:10, ]
    plt.figure(figsize=(9, 5))
    pal = reversed(sns.color_palette("bone", 10))
    sns.barplot(df.values, df.index, palette=pal)

    plt.title('@' + username + "'s most used words")
    plt.ylabel('Word or Word Stem', fontsize=10)
    plt.xlabel('Frequency', fontsize=10)
    plt.tight_layout()

    # convert and return base64 image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img64 = base64.b64encode(img.read()).decode()
    return img64


@app.route("/")
def index():
    return "Endpoint works"


@app.route('/sub/', methods=['POST'])
def empty():
    return "OMG"
    return {'status': 404}


@app.route('/sub/<username>', methods=['POST'])
def sub(username):
    if username[0] == '@':
        username = username[1:len(username)]
        print(username)
    resp = verifyUser(username)
    if resp:
        words = get_words(resp, username)
    else:
        return {'status': 404}
    print("went ok")
    return {'status': 200, 'image': words}


def verifyUser(username):
    consumer_key = "8JMkNLDQTOMNuJ9kZBMY3d0Z4"
    consumer_secret = "GzaJND9EAntOj1Wyms2JXDwXbVjLBfkBo16HyqUdFba8tyBxMX"
    access_token = "1337134855050547200-5j3GYiKTHphlYLIPgnGLFQtKbXBW6N"
    access_token_secret = "RRHcvpuH4jJ75h4JjwZe9YgQL5OgQDtRDTL7ptykksH8q"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    try:
        username = username
        api = tweepy.API(auth)

        timeline = api.user_timeline(username, count=200)

        return timeline
    except tweepy.TweepError:
        print("No such username found. Please try again.")
        return None


if __name__ == "__main__":
    app.run()
