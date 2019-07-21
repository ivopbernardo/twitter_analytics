import pandas as pd
import matplotlib.pyplot as plt

#My example, use you local files by company to plot them
companies = ['nike','adidas']

reviews = {}

exec=1
for f in companies:
    reviews[f]= pd.read_csv(f+'.csv')
    if exec == 1:
        sentiment_table = reviews[f]
        sentiment_table['company'] = f
    else:
        aux_sentiment_table = reviews[f]
        aux_sentiment_table['company'] = f
        sentiment_table = sentiment_table.append(aux_sentiment_table)
    exec += 1

field = "Sentiment"
day_order = ["Positive", "Neutral", "Negative"]
table = sentiment_table.groupby(['Sentiment','company']).aggregate('count').iloc[:,0].unstack()
ax = table.loc[day_order].plot(kind="bar", edgecolor='black', color = ['#ccccff','#ffd9b3'])
ax.set_ylabel("Tweet Count")
plt.tight_layout()
plt.show()

