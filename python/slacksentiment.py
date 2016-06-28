
#!/usr/bin/env python

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from slacker import Slacker
from elasticsearch import Elasticsearch
import json
import datetime

slack = Slacker('redact')
sid = SentimentIntensityAnalyzer()
es = Elasticsearch('redact:80')

# get users in the #general channel so we can attribute names
users={}

for member in slack.users.list().body['members']:
    users[member['id']] = member

# get each channel
for channel in slack.channels.list().body['channels']:

    # get messages in each channel 
    messages = slack.channels.history(channel=channel['id'], oldest="1465516800.000000").body['messages']

    for message in messages:
        timestamp = message['ts'].decode("utf-8").split('.')[0]
        user = message['user']
        sentences = tokenize.sent_tokenize(message['text'])
        compoundSentiment = 0;
        for sentence in sentences:
            print(sid.polarity_scores(sentence))
            compoundSentiment += sid.polarity_scores(sentence)['compound']/len(sentences)
        message['sentiment'] = compoundSentiment
        message['timestamp'] = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        message['username'] = users[user]['name']
        message['channelid'] = channel['id']
        message['channelname'] = channel['name']
        #message['fullname'] = users[user]['first_name']+" "+users[user]['last_name']
        print json.dumps(message)
        es.index(index='nltkdemo', doc_type="slack", id=message['ts'], body=message)
