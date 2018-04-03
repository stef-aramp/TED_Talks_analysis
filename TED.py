#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 20:41:30 2018

@author: stephanosarampatzes
"""

# import basic libraries
import numpy as np
import pandas as pd

# load data csv
df = pd.read_csv('ted_main.csv')
df.info()

# keep url in separate series
urls = df.url
urls[:2]

# drop some columns
df = df.drop(['name', 'url', 'related_talks'], axis = 1)

# check for missing values 
# isNull() -> isna() Pandas 0.22
df.isna().sum()

# drop NAs and reset index
df = df.dropna()
df = df.reset_index(drop = True)

# convert sec to mins
df['duration'] = df['duration'].apply(lambda x: round(x/60.0, 1))
df['duration'][:2]

# RATINGS #
print(df.ratings[:3],"\n",df.ratings[-3:])

# RATINGS #
from ast import literal_eval

# sort ratings by count
df.ratings = df['ratings'].apply(lambda x: literal_eval(x))
df.ratings = df.ratings.apply(lambda x: sorted(x, key=lambda k: k['count'], reverse=True))

# we need name...
df['top_rate'] = df.ratings.apply(lambda x: x[0]['name'])

# ...and count
df['top_rate_count'] = df.ratings.apply(lambda x: x[0]['count'])

# top rates
print('Top ratings')
df.top_rate.value_counts()

for i in ['Inspiring','Informative','Funny','Ingenious','Jaw-dropping','Unconvincing','Confusing']:
    print("\n|",i,"\n")
    print(df.loc[df.top_rate == i,
                 ['top_rate','top_rate_count','title','main_speaker']].sort_values('top_rate_count', ascending = False)[:5])

# import visualization libraries

import seaborn as sns
import matplotlib.pyplot as plt

# TAGS
df.tags = df.tags.apply(lambda x: literal_eval(x))

# collect tags in a list
tags = []
for i in df.tags:
    for j in i:
        tags.append(j)

# Counter: tool for most frequent elements in a list
from collections import Counter

# Top 20 tags
count_tags = Counter(tags).most_common(20)
count_tags=dict(count_tags)

# FUNCTION FOR BARPLOTS

def barplot(x, y, xlabel, ylabel, title, palette):
    fig,ax = plt.subplots(figsize=(12, 10))
    sns.barplot(x, y, palette = palette)
    plt.xticks(rotation = 80, fontsize =14)
    plt.xlabel(xlabel, fontsize = 13)
    plt.yticks(fontsize = 11)
    plt.ylabel(ylabel, fontsize = 13)
    plt.title(title, fontsize = 15)
    return(plt.show())

# Top20 Tags
barplot(list(count_tags.keys()), list(count_tags.values()), 'Tags', 'Counts', 'Top 20 Tags', 'Paired')

### Manipulate DATES
# convert unix time to timestamp for film date and publish date

from datetime import datetime

# convert film_date column
df.film_date = df.film_date.apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
df.film_date = df.film_date.apply(lambda x: datetime.strptime(x,'%Y-%m-%d'))

# convert published_date column
df.published_date = df.published_date.apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
df.published_date = df.published_date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

# Create a new column with "date difference" in days
df['date_diff'] = df.published_date - df.film_date
df['date_diff'] = df.date_diff.apply(lambda x: x.days)

df[['film_date','published_date','date_diff']][:5]

# check for negative remainder
df.loc[df.date_diff < 0,['film_date','published_date','date_diff']]

# Handle dates with negative diff.

# SWAP values
df.loc[df.index == 614, ['film_date', 'published_date']] = df.loc[df.index == 614, ['published_date', 'film_date']].values
df.loc[df.index == 1490, ['film_date', 'published_date']] = df.loc[df.index == 1490, ['published_date', 'film_date']].values
df.loc[df.index == 1842, ['film_date', 'published_date']] = df.loc[df.index == 1842, ['published_date', 'film_date']].values

# change month in publish date
df['published_date'][857] = df['published_date'][857].replace(month = 9)

# change year
for i in range(323,329):
    df['published_date'][i] = df['published_date'][i].replace(year = 2009)

# check for errors

df['date_diff'] = df.published_date - df.film_date
df['date_diff'] = df.date_diff.apply(lambda x: x.days)

print(df.loc[df.date_diff < 0,['film_date','published_date','date_diff']])

# FUNCTION for jointplots

def pointplot(x, y, xlabel, ylabel, title, color):
    fig,ax = plt.subplots(figsize = (12,10))
    sns.pointplot(x, y, color = color, linestyles="--")
    plt.xlabel(xlabel, fontsize = 13)
    plt.ylabel(ylabel, fontsize = 14)
    plt.title(title, fontsize = 15)
    return(plt.show())

# film date - views
df['f_year'] = df['film_date'].apply(lambda x: x.year)
flm_views = df[['f_year','views']].groupby('f_year').sum().apply(lambda x: round(x/1000000, 2)).reset_index()

# plot
pointplot(flm_views.f_year, flm_views.views, 'Year', 'Views in millions', 'Total views per film year', '#ff474c')

# total views from talks per year

print('Total views per year:')
flm_views.sort_values('views', ascending = False)[:10]

# pubplished date - views

df['p_year'] = df['published_date'].apply(lambda x: x.year)
pub_views = df[['p_year','views']].groupby('p_year').sum().apply(lambda x: round(x/1000000, 2)).reset_index()

# plot
pointplot(pub_views.p_year, pub_views.views, 'Year', 'Views in millions', 'Total views per film year', '#0165fc')

# published_date views
pub_views.sort_values('views', ascending = False)[:5]

# biggest number of talks per day since day 1
df.film_date.value_counts()[:5]

# year with biggest number of talks / plot below
df.f_year.value_counts()[:10]

# top tags by year
df[['f_year','tags']].groupby('f_year').agg('max')[-15:]

# year with biggest number of publishments
df.p_year.value_counts()[:7]

# films per year
# countplot
fig,ax = plt.subplots(figsize = (12,10))
sns.countplot(df.f_year, palette='deep')
plt.xlabel('Year', fontsize = 14)
plt.ylabel('Number of films', fontsize = 14)
plt.title('Total films per year', fontsize = 15)
plt.show()

# correlation
df[['views','comments','duration']].corr()

# views - comments
import warnings
sns.jointplot(df.views, df.comments, kind = 'reg')
plt.show()

# views - duration
sns.jointplot(df.views, df.duration, kind = 'reg')
plt.show()

### TOP TEN

# most viewed
df[['views','main_speaker','title','languages','comments']].sort_values('views', ascending = False)[:10]

# most commented
df[['comments','main_speaker','title','film_date','published_date']].sort_values('comments', ascending = False)[:10]

# longest duration in minutes
df[['duration','main_speaker', 'title']].sort_values('duration', ascending = False)[:10]

# most translated
df[['languages','main_speaker','title']].sort_values('languages', ascending = False)[:10]

# too late ... "please upload"!!!  Top 20
df[['date_diff','title','main_speaker','film_date','published_date','views','event']].sort_values('date_diff', ascending = False)[:20]

# most common speaker's occupation
# split the "multi-talented" speakers to their main occupation

df.speaker_occupation = df.speaker_occupation.apply(lambda x: x.split(',')[0])
df.speaker_occupation.value_counts()[:10]

# plot for speaker's occupation

barplot(df.speaker_occupation.value_counts().reset_index()[:10]['index'],
        df.speaker_occupation.value_counts().reset_index()[:10]['speaker_occupation'],
       'Occupation','Count',"Counts per speaker's occupation","coolwarm")

# top speakers of all time based on appearances
df.main_speaker.value_counts()[:10]

# Top speakers of all time based on appearances
barplot(df.main_speaker.value_counts().reset_index()[:15]['index'],
        df.main_speaker.value_counts().reset_index()[:15]['main_speaker'],
       "Speaker's Name",'Appearances','Top speakers of all time based on appearances',"RdBu_r")

# occupation of top speakers
for i in df.main_speaker.value_counts()[:10].reset_index()['index']:
    print(i,df.loc[df.main_speaker == i, ['speaker_occupation']].agg('max'))

# talks with more than 1 speaker
df.loc[df.num_speaker > 1,['title', 'event','num_speaker', 'main_speaker']].sort_values('num_speaker', ascending = False)

# NUMERICAL FEATURES ANALYSIS
# FUNCTION for distplots

def distplot(column, title):
    fig,ax = plt.subplots(figsize = (10,10))
    sns.distplot(column)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)
    plt.title(title, fontsize = 15)
    return(plt.show())

def stats(column):
    return('mean:',round(column.mean(),2), 'median:', round(column.median(),2), 'std:', round(column.std(),2),
           'min:', column.min(), 'max:', column.max())

# we can simply type eg.  df.views.describe() and see the Q1 and Q3 values

# views
stats(df.views)

# distribution of views
distplot(df.views, 'views')
plt.show()

###  ! Seaborn causes the warning. Nothing to do here, seaborn patch should be released soon !

fig,ax = plt.subplots(figsize = (15,9))
sns.boxplot(df.views)
plt.show()

# talks with more than 10M views (avg =1.7M !)
df.loc[df.views > 1e07, ['title']].agg('count')

# views under 10M - a better insight
distplot(df.loc[df.views < 1e07, ['views']], 'closer views')

# comments
stats(df.comments)

# Distribution of comments
distplot(df.comments, 'comments')

fig,ax = plt.subplots(figsize = (15,9))
sns.boxplot(df.comments)
plt.show()

distplot(df.loc[df.comments < 500, ['comments']], 'comments')

# duration
stats(df.duration)
# in minutes

distplot(df.duration, 'duration')

fig,ax = plt.subplots(figsize = (15,9))
sns.boxplot(df.duration)
plt.show()

distplot(df.loc[df.duration < 25, ['duration']], 'duration < 25 mins')

# languages
stats(df.languages)

distplot(df.languages, 'languages')

### WORDCLOUD
# import wordcloud
from wordcloud import WordCloud

# import regular expressions
import re

# punctuation
from string import punctuation

# Merge title and description
df['text'] = df.title + ' ' + df.description 

# create corpus
words = []
for i in df.index:
    text = re.sub('[^a-zA-Z]',' ', df.text[i]).lower()
    word = [w for w in text if w not in set(list(punctuation))]
    word = ''.join(word)
    words.append(word)    

# convert list of strings to a single huge string
words = ' '.join(words)

# 1
wordcloud = WordCloud(background_color="white").generate(words)
plt.figure(figsize = (12, 10))
plt.imshow(wordcloud, interpolation = 'bilinear')
plt.title('Most Frequent Words', fontsize = 15)
plt.axis("off")
plt.show()

# 2
wordcloud = WordCloud(background_color="white",max_font_size = 40).generate(words)
plt.figure(figsize = (12, 10))
plt.imshow(wordcloud, interpolation="bilinear")
plt.title('Most Frequent Words (fontsize limit)', fontsize = 15)
plt.axis("off")
plt.show()

# END OF STORY