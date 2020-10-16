import tweepy
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
from dotenv import load_dotenv
import os
import sqlite3
from textblob import TextBlob
import json
from unidecode import unidecode
import time


conn = sqlite3.connect('twitter.db')
c = conn.cursor()


def create_table():
    try:
        c.execute(
            "CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))


create_table()
load_dotenv()


class Listener(StreamListener):
    def on_status(self, status):
        try:
            tweet = unidecode(status.text)
            time_ms = status.timestamp_ms
            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity

            print(time_ms, tweet, sentiment)

            c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (time_ms, tweet, sentiment))
            conn.commit()

        except KeyError as e:
            print(str(e))

        return True

    def on_error(self, status):
        if status == 420:
            print("Rate Limited, Disconnecting...")
            return False
        print(status)


while True:
    try:
        auth = OAuthHandler(consumer_key=os.getenv('CONSUMER_KEY'),
                            consumer_secret=os.getenv('CONSUMER_SECRET'))
        auth.set_access_token(key=os.getenv('ACCESS_TOKEN'),
                              secret=os.getenv('ACCESS_SECRET'))
        api = tweepy.API(auth)
        stream_listener = Listener()
        twitter_stream = Stream(auth=auth, listener=stream_listener)
        twitter_stream.filter(track=['a', 'e', 'i', 'o', 'u'])
    except Exception as e:
        print(str(e))
        time.sleep(5)
