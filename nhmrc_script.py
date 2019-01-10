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
    url = base_url + "q={q}&count={count}&result_type={result_type}&lang={lang}&since_id={since_id}&tweet_mode={tweet_mode}".format(**payload)
    r = requests.get(url, auth=auth)
    tweets = r.json()["statuses"]
    return tweets




#---------------------------------------------------------------------
# search function - takes keyword and organisation lists - returns tweet list
#---------------------------------------------------------------------
def search_api(keyword_list):
    
    all_tweets = []
    for keyword in keyword_list:
        print('Searching for {}'.format(keyword))
        
        
        since_id = -1
        tweet_list = []
        tweet_id_list = []
        count = 0
        while count < 2: #300 tweets per search
            try: 
                # create list of tweet ids already found 
                tweet_id_list = [tweet_list[x]['id'] for x in range(0, len(tweet_list))]
                # call twitter api and search for keyword
                tweets = find_tweets(keyword,  since_id=since_id)
                print('{} tweets found'.format(len(tweets)))

                # add new tweets to list
                for t in tweets:
                    if t['id'] not in  tweet_id_list:
                        tweet_list.append(t)

                # update since id
                since_id = tweets[0].get('id')
                count +=1
                # add new tweets to list of tweets for search item1
                for tweet in tweet_list:
                    all_tweets.append(tweet)
                    
            except Exception as e:
                time.sleep(15)
                # stops loop
                count +=2
                #print("exception - no tweets found")
        print('Search completed')
    
    return all_tweets    
        
        
#---------------------------------------------------------------------
# Twitter parameters
#---------------------------------------------------------------------
base_url = "https://api.twitter.com/1.1/search/tweets.json?"
payload = dict(
count = 50,
result_type = 'mixed',
lang = 'en',
tweet_mode = 'extended')



keywords = ['Government+AND+%20Policy+OR+%20Funding+OR+%20NHRMC+OR+%20Research+OR+%20Medical+OR+%20Health+OR+%20Grant',
            'Medical+AND+%20Policy+OR+%20Funding+OR+%20NHRMC+OR+%20Research+OR+%20Health+OR+%20Grant',

            'Research+AND+%20Policy+OR+%20Funding+OR+%20NHRMC+OR+%20Health+OR+%20Grant',

            'Policy+AND+%20Funding+OR+%20NHRMC+OR+%20Health+OR+%20Grant',

            'Funding+AND+%20NHRMC+OR+%20Health+OR+%20Grant',
            
            'Grant+AND+%20NHRMC+OR+%20Health'
            
            'National%20Medical%20Health%20Research%20Council',
            
            'Government+OR+%20Policy+OR+%20Funding+OR+%20NHRMC+OR+%20Research+OR+%20Medical+OR+%20Health+OR+%20Grant' ]

single_keywords = ['Government','Policy','Funding','NHRMC',
                   'Research','Medical','Health','Grant',
                   'National%20Medical%20Health%20Research%20Council']

organisations = ['QIMRBerghofer',
                 'GarvanInstitute',
                 'WEHI_research',
                 'MCRI_for_kids',
                 'BakerResearchAu',
                 'blackdoginst',
                 'CentenaryInst',
                 'jeansforgenesau',
                 'TheFlorey',
                 'sahmriAU',
                 'WestmeadInst',
                 'PeterMacCC',
                 'EyeResearchAus',
                 'unimelb',
                 'ANUmedia',
                 'UNSW',
                 'MonashUni',
                 'Sydney_Uni',
                 'uwanews',
                 'UniversitySA',
                 'UQ_News',
                 'UniofAdelaide',
                 'UTSEngage',
                 'UTAS_',
                 'Flinders',
                 'Uni_Newcastle',
                 'UOW',
                 'QUT',
                 'latrobe',
                 'Macquarie_Uni']

#---------------------------------------------------------------------
# search for keywords
#---------------------------------------------------------------------
#keyword_list = ['unimelb%20student']

# directed to/from user -> q=to%3Ajohnqpublic to%3A  from%3A
# find by hashtag - %23
# mentions -> %40

#key_to_org_list = ['to%3A'+o+'%20'+ k for o in organisations for k in single_keywords]
#key_to_org_tweets = search_api(key_to_org_list)

#key_from_org_list = ['from%3A'+o+'%20'+k for o in organisations for k in single_keywords]
#key_from_org_tweets = search_api(key_from_org_list)

#hash_to_org_list = ['to%3A'+o+'%20%23'+k for o in organisations for k in single_keywords]
#hash_to_org_tweets = search_api(hash_to_org_list)

#hash_from_org_list = ['from%3A'+o+'%20%23'+k for o in organisations for k in single_keywords]
#hash_from_org_tweets = search_api(hash_from_org_list)

#key_ment_org_list = ['%20%40'+o+'%20'+k for o in organisations for k in single_keywords]
#key_ment_org_tweets = search_api(key_ment_org_list)

#hash_ment_org_list = ['%20%40'+o+'%20%23'+k for o in organisations for k in single_keywords]
#hash_ment_org_tweets = search_api(hash_ment_org_list)

all_tweets_list = [o+'%20'+k for o in organisations for k in single_keywords]
all_tweets = search_api(all_tweets_list)
# print length of each list - count tweets returned
