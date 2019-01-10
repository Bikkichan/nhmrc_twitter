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


auth = OAuth1(config.consumer_key, 
config.consumer_secret, 
config.access_key, 
config.access_secret)

base_url = "https://api.twitter.com/1.1/search/tweets.json?"

url = base_url + "q=aesop&count=100&result_type=recent&lang=en&since_id=-1"

r = requests.get(url, auth=auth)

# all tweets
r.json()['statuses']

# keys
r.json()['statuses'][0].keys()

# access tweet details
for tweet in r.json()['statuses']:
    print(tweet['user']['name'])