import os
import sys
import signal
import time
import requests
from requests_oauthlib import OAuth1
# API authorisation 
import twitter
import sys
sys.path.append(".")
import config

#---------------------------------------------------------------------
#  Exit script gracefully
#---------------------------------------------------------------------
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#---------------------------------------------------------------------
#  neo4j parameters
#---------------------------------------------------------------------
from py2neo import Graph, Node, Relationship
graph = Graph(host='127.0.0.1', port=7687, scheme='bolt', user='neo4j', password='password')	
graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.username IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (t:Tweets) ASSERT t.id IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE")
#---------------------------------------------------------------------
# Twitter authorisation
#---------------------------------------------------------------------
auth = OAuth1(config.consumer_key, 
config.consumer_secret, 
config.access_key, 
config.access_secret)
#---------------------------------------------------------------------
# function to request tweets from api
#---------------------------------------------------------------------
def find_tweets(keyword, since_id):
    payload['q'] = keyword
    payload['since_id'] = since_id
    url = base_url + "q={q}&count={count}&result_type={result_type}&lang={lang}&since_id=-1".format(**payload)
    r = requests.get(url, auth=auth)
    tweets = r.json()["statuses"]
    return tweets
#---------------------------------------------------------------------
# upload to neo4j
#---------------------------------------------------------------------
def upload_to_graph(tweet_list):
    for t in tweet_list:
        u = t["user"]
        e = t["entities"]
       # Tweet node
        tweet_node = Node("Tweets", id=t["id"])
        graph.merge(tweet_node, "Tweets", "id")
        tweet_node["text"] = t["text"]
        graph.push(tweet_node)
        # User node
        user_node = Node("User", username=u["screen_name"])
        graph.merge(user_node, "User", "username")
        rel = Relationship(user_node, "POSTS", tweet_node)
        graph.merge(rel)
    
        for h in e.get("hashtags",[]):
            hashtag_node = Node("Hashtag", name=h["text"].lower())
            graph.merge(hashtag_node, "Hashtag", "name")
            rel = Relationship(tweet_node, "MENTIONS", hashtag_node)
            graph.merge(rel)
        reply = t.get("in_reply_to_status_id")
        if reply:
            reply_tweet = Node("Tweets", id=reply)
            graph.merge(reply_tweet, "Tweets", "id")
            rel = Relationship(tweet_node, "REPLY_TO", reply_tweet)
        ret = t.get("retweeted_status", {}).get("id")
        if ret:
            retweet_node = Node("Tweets", id=ret)
            graph.merge(retweet_node, "Tweets", "id")
            rel = Relationship(tweet_node, "RETWEETS", retweet_node)
            graph.merge(rel)
#---------------------------------------------------------------------
# search for tweets and upload to graph
#---------------------------------------------------------------------
def keyword_search_upload(keyword):
    since_id = -1
    tweet_list = []
    retry_count = 0
    while retry_count < 2:
        try: 
            # create list of tweet ids already found 
            tweet_id_list = [tweet_list[x]['id'] for x in range(0, len(tweet_list))]
            # call twitter api and search for keyword
            tweets = find_tweets(keyword,  since_id=since_id)
            # if no tweets found
            if len(tweets) == 0:
                print("No tweets found.")
                retry_count +=2
                print('sleeping...')
                time.sleep(15)
                #try again
                continue
                print('continuing!')
            # if tweet id is not in list 
            # then add the tweet to the tweet list
            count = 0
            for t in tweets:
                if t['id'] not in  tweet_id_list:
                    count +=1
                    tweet_list.extend(tweets)
            # if there are new tweets
            # then upload them to the graph
            if count > 0:
                print('{} tweets found!'.format(len(tweets)))
                print('New tweets added to list')
                upload_to_graph(tweet_list)
                print('Uploading tweets to graph') 
                print('sleeping...')       
                time.sleep(15)
            else:
                print('No new tweets found...')
                retry_count +=1
                time.sleep(15)
            
            since_id = tweets[-1].get('id')
            
        except Exception as e:
            print("exception", e)
            print('sleeping...')
            time.sleep(15)
            continue    
            print('continuing!')
    else:
        print('Search completed! ')
#---------------------------------------------------------------------
# Twitter parameters
#---------------------------------------------------------------------
base_url = "https://api.twitter.com/1.1/search/tweets.json?"
payload = dict(
count = 100,
result_type = 'mixed',
lang = 'en')
#---------------------------------------------------------------------
# delete everythin in graph before starting 
#---------------------------------------------------------------------
graph.delete_all()
print('All graph entries deleted')
#---------------------------------------------------------------------
# search for keywords
#---------------------------------------------------------------------
keyword_list = ['%23aesopskincare', 'aesopskincare', 'aesop-au']
for keyword in keyword_list:
    print('Searching for {}'.format(keyword))
    keyword_search_upload(keyword)