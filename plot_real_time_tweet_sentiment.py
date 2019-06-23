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

#Keys for Twitter API 
ckey='your ckey'
csecret = 'your csecret'
atoken= 'your atoken'
asecret= 'your asecret'

#Provide word to query twitter
word = input("Hello! Which word do you want to track? \n")

#Read text data for Sentiment Analysis - Positive and Negative Words
def read_text_files(file):
    list_of_words = []
    f = open(file)
    for line in f:
        list_of_words.append(line)
    
    list_of_words = list(map(lambda s: s.strip(), list_of_words))
    list_of_words = list_of_words[31:]
    return list_of_words

pos_words = read_text_files('positive-words.txt')
neg_words = read_text_files('negative-words.txt')

#Function for Handling Tweet
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)     
    return input_txt  

#Empty tweet_list and sentiment list assignment
tweets_list = []
sents = []

#Attribute color to tweet according to sentiment distribution, for each Neutral, Negative, Positive combination
def dataframe_assign_colors(table):
    if len(table.Sentiment.str.get_dummies().sum().index) == 1:
        if (table.Sentiment.str.get_dummies().sum().index)[0] == "Neutral":
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['grey'] )
        elif (table.Sentiment.str.get_dummies().sum().index)[0] == "Negative":
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['red'] )
        else:
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['green'] )
    elif len(table.Sentiment.str.get_dummies().sum().index) == 2:
        if ((table.Sentiment.str.get_dummies().sum().index)[0] == "Negative" and (table.Sentiment.str.get_dummies().sum().index)[1] == "Neutral"):
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['red','grey'] )
        elif ((table.Sentiment.str.get_dummies().sum().index)[0] == "Negative" and (table.Sentiment.str.get_dummies().sum().index)[1] == "Positive"):
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['red','green'] )
        else:
                table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
                colors = ['grey','green'] )  
    else:
        table.Sentiment.str.get_dummies().sum().plot.pie(label=company+ ' Twitter Sentiment', autopct='%1.0f%%',
        colors = ['red','grey','green'] )        

#Get tweet and sentiment by tweet filtering the words with the 'word' parameter
class listener(StreamListener):
    def on_data(self, data):
        try:
            text_tweet = json.loads(data)['text']  
            print(text_tweet)
            new_tweet = str((np.vectorize(remove_pattern)(text_tweet, "@[\w]*")))
            new_tweet=re.sub(r'[^A-Za-z0-9]+', ' ', new_tweet)
            new_tweet = new_tweet.replace("RT", "")                          
            tokenized_tweet = new_tweet.split()
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
            #This is optional for printing the data frame with tweets plus sentiment - comment it for no dataframe output
            print(tweets_df)
            #Choose the parameters of the numpy array for deciding the interval to plot the sentiment. With the current settings you will plot the distribution in the pie plot for each 20 tweets, starting from tweet number 10 until tweet number 1100
            if len(tweets_df) in np.arange(10,1100,20):
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

#Using authentication parameters to get twitter data and using the Stream from tweepy to get real time tweets
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=[word])

