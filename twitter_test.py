import twitter
import sys
sys.path.append(".")
import config
#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
api = twitter.Api(config.consumer_key, config.consumer_secret, config.access_key, config.access_secret)
print(api)
print(api.VerifyCredentials())	

#-----------------------------------------------------------------------
# search by key word; returns list of tweets
#-----------------------------------------------------------------------
search = api.GetSearch("happy") 
for tweet in search:
    # tweet type == twitter.models.Status
    print(tweet.id, tweet.text)	
	
# list of dictionary for search results
search_dict = [s.AsDict() for s in search]

#-----------------------------------------------------------------------
# search for tweets by user
#-----------------------------------------------------------------------
t = api.GetUserTimeline(screen_name="akras14", count=10)
# returns list

#print id and text of each tweet
for tweet in tweets:
    print(tweet['id'], tweet['text'])
	
# convert each tweet into dictionary in list
tweets = [i.AsDict() for i in t]   # i type == twitter.models.Status


