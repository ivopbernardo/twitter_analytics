from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import re
import string
import pandas as pd
import time
import traceback
import os
from nltk.corpus import stopwords

#Set stop words
stop_words = set(stopwords.words('english')) 

#Keys for Twitter API 
ckey='YOUR CKEY'
csecret = 'YOUR CSECRET'
atoken= 'YOUR ATOKEN'
asecret= 'YOUR ASECRET'

company = input("Hello! Which company do you want to check? \n")

def read_text_files(file):
    list_of_words = []
    f = open(file)
    for line in f:
        list_of_words.append(line)
    
    list_of_words = list(map(
        lambda s: s.strip(), list_of_words)
    )
    list_of_words = list_of_words[31:]
    return list_of_words

#Text Data for Sentiment Analysis - Positive and Negative Words
pos_words = read_text_files('positive-words.txt')
neg_words = read_text_files('negative-words.txt')

#Function for Handling Tweet

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
        
    return input_txt  

tweets_list = []
sents = []

def dataframe_assign_colors(table):
    if len(table.Sentiment.str.get_dummies().sum().index) == 1:
        if (table.Sentiment.str.get_dummies().sum().index)[0] == "Neutral":
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',startangle=90,
                colors = ['#d6e2d5'] )
        elif (table.Sentiment.str.get_dummies().sum().index)[0] == "Negative":
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
                colors = ['#ff9999'] )
        else:
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
                colors = ['#99ff99'] )
    elif len(table.Sentiment.str.get_dummies().sum().index) == 2:
        if ((table.Sentiment.str.get_dummies().sum().index)[0] == "Negative" and (table.Sentiment.str.get_dummies().sum().index)[1] == "Neutral"):
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
                colors = ['#ff9999','#d6e2d5'] )
        elif ((table.Sentiment.str.get_dummies().sum().index)[0] == "Negative" and (table.Sentiment.str.get_dummies().sum().index)[1] == "Positive"):
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
                colors = ['#ff9999','#99ff99'] )
        else:
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
                colors = ['#d6e2d5','#99ff99'] )  
    else:
        table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%', startangle=90,
        colors = ['#ff9999','#d6e2d5','#99ff99'] )        

class listener(StreamListener):
    def on_status(self, status):
        try:
            #Add validation for full text. If it does not exist text is a retweet and we want to get 'text' instead
            try:
                text_tweet = status.extended_tweet['full_text']
            except:
                text_tweet = status.text
            new_tweet = str((np.vectorize(remove_pattern)(text_tweet, "@[\w]*")))
            new_tweet=re.sub(r'[^A-Za-z0-9]+', ' ', new_tweet)
            new_tweet = new_tweet.replace("RT", "")                          
            tokenized_tweet = new_tweet.split()
            tokenized_tweet = [x for x in tokenized_tweet if x not in stop_words]
            tokenized_tweet = list(map(lambda s:s.lower(),tokenized_tweet))
            nb_pos_words = [x for x in tokenized_tweet if x in pos_words]
            nb_neg_words = [x for x in tokenized_tweet if x in neg_words]
            score = len(nb_pos_words)-len(nb_neg_words)
            if score >= 1:
                sentiment = "Positive"
            elif score == 0:
                sentiment = "Neutral"
            else:
                sentiment = "Negative"
            tweets_list.append(text_tweet)
            sents.append(sentiment)
            tweets_df = pd.DataFrame({'Tweets':tweets_list, 'Sentiment':sents})
            tweets_df.to_csv(company+'.csv')
            if len(tweets_df) in np.arange(10,1100,20):
                print(tweets_df)
                plt.figure()
                dataframe_assign_colors(tweets_df)
                plt.show(block=False)
                plt.pause(3)
                plt.close('all') 
            return True
        except BaseException as e:
            print (e)
            print(traceback.format_exc())
    def on_error(self, status):
        print (status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener(), tweet_mode='extended')
twitterStream.filter(track=[company])

