import os
import sys
import time
import requests
from requests_oauthlib import OAuth1

from py2neo import Graph, Relationship, Node

# API authorisation 
import twitter
import sys
sys.path.append(".")
import config

# Neo4j auth
NEO4J_USERNAME =  "neo4j"
NEO4J_PASSWORD = "password"
 
# if NEO4J_USERNAME and NEO4J_PASSWORD:
    # authenticate('localhost:7474', NEO4J_USERNAME, NEO4J_PASSWORD)

graph = Graph( bind={"user":NEO4J_USERNAME, "password":NEO4J_PASSWORD})
print("instantiating graph")

# Twitter auth
# create twitter API object
api = twitter.Api(config.consumer_key, 
config.consumer_secret, 
config.access_key, 
config.access_secret)

auth = OAuth1(config.consumer_key, 
config.consumer_secret, 
config.access_key, 
config.access_secret)

# headers = dict(
        # accept='application/json',
        # Authorization='Bearer ' + TWITTER_BEARER)

payload = dict(
    count=100,
    result_type="recent",
    lang="en")

base_url = "https://api.twitter.com/1.1/search/tweets.json?"

def find_tweets(keyword, since_id):
    payload['q'] = keyword
    payload['since_id'] = since_id

    url = base_url + "q={q}&count={count}&result_type={result_type}&lang={lang}&since_id={since_id}".format(**payload)
    print(url)
    r = requests.get(url, auth=auth)
    tweets = r.json()["statuses"]

    return tweets

def upload_tweets(tweets):
    for t in tweets:
        u = t["user"]
        e = t["entities"]

        # tweet = Node(label=	"Tweet", id=t["id"])
        tweet = Node("Tweet", id=t["id"])
        print(tweet, "Tweet", t["id"])
		
        tw = graph.merge(tweet, "Tweet", t["id"])
        print(tw)
        tw["text"] = t["text"]
        graph.push(tw)

        user = Node("User", username=u["screen_name"])
        graph.merge(user)

        graph.merge(Relationship(user, "POSTS", tweet))

        for h in e.get("hashtags", []):
            print('hashtags')
            hashtag = Node("Hashtag", name=h["text"].lower())
            graph.merge(hashtag)
            graph.merge(Relationship(hashtag, "TAGS", tweet))

        for m in e.get('user_mentions', []):
            print('user_mentions')
            mention = Node("User", username=m["screen_name"])
            graph.merge(mention)
            graph.merge(Relationship(tweet, "MENTIONS", mention))

        reply = t.get("in_reply_to_status_id")

        if reply:
            print('reply')
            reply_tweet = Node("Tweet", id=reply)
            graph.merge(reply_tweet)
            graph.merge(Relationship(tweet, "REPLY_TO", reply_tweet))

        ret = t.get("retweeted_status", {}).get("id")

        if ret:
            retweet = Node("Tweet", id=ret)
            graph.merge(retweet)
            graph.merge(Relationship(tweet, "RETWEETS", retweet))
    
    graph.commit()
    print('Upload tweets to graph')

graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.username IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE")

since_id = -1

while True:
    try:
        tweets = find_tweets(sys.argv[1], since_id=since_id)
        if len(tweets) == 0:
            print("No tweets found.")
            time.sleep(60)
            continue
        since_id = tweets[0].get('id')
        
        upload_tweets(tweets)
        print(str(len(tweets)) +  " tweets uploaded!")
        time.sleep(60)
    except Exception as e:
        print("exception", e)
        time.sleep(60)
        continue