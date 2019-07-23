import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from nltk.corpus import stopwords
import numpy as np
import os
import pandas as pd
import re
import string
import traceback
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

#Set stop words
stop_words = set(stopwords.words('english')) 

#Keys for Twitter API 
ckey='YOUR CKEY'
csecret = 'YOUR CSECRET'
atoken= 'YOUR ATOKEN'
asecret= 'YOUR ASECRET'

company = input("Hello! Which company do you want to check? \n")

def read_text_files(file: str) -> list:
    ''' Reads text files for positive and negative words'''
    list_of_words = []
    
    with open(file, 'r') as f:
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

#Function for Handling Tweet and Clean Pattern
def remove_pattern(input_txt: str, pattern: str) -> str: 
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
        
    return input_txt  

tweets_list = []
sents = []

def dataframe_assign_colors(table: pd.DataFrame):
    '''Assigns colors to Neutral, Negative and Positive sentiment plot - Probably there is a cleaner way to do this'''
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
            #Pre-Processing phase, remove retweets and user mentions - also retain only characters or numbers
            new_tweet = str((np.vectorize(remove_pattern)(text_tweet, "@[\w]*")))
            new_tweet=re.sub(r'[^A-Za-z0-9]+', ' ', new_tweet)
            new_tweet = new_tweet.replace("RT", "")   
            #Split tweet into a list, remove stop words and lowercase all characters                       
            tokenized_tweet = new_tweet.split()
            tokenized_tweet = [x for x in tokenized_tweet if x not in stop_words]
            tokenized_tweet = list(map(lambda s:s.lower(),tokenized_tweet))
            #Lookup number of positive and negative words and compute score
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
            #Create new dataframe from the list of tweets and sentiment 
            tweets_df = pd.DataFrame({'Tweets':tweets_list, 'Sentiment':sents})
            tweets_df.to_csv(company+'.csv')
            #Plot pie chart for every 20 tweets
            if len(tweets_df) in np.arange(10,1100,20):
                print(tweets_df)
                plt.figure()
                dataframe_assign_colors(tweets_df)
                plt.show(block=False)
                plt.pause(3)
                plt.close('all') 
            return True
        except BaseException as e:
            print(e)
            print(traceback.format_exc())
    def on_error(self, status):
        print (status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener(), tweet_mode='extended')
twitterStream.filter(track=[company])

