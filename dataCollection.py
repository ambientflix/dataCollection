import sys, tweepy
import re
import string
import requests
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
from newsapi import NewsApiClient
import json
#import twecoll

# Authorizes access to the Twitter API
def twitter_auth():
    try:
        consumer_key = "DSt3NyAqOGFEGyUWzLRYZcx1g"
        consumer_secret = "581Fs2Q0hDctuMISQ83EkNp8xwc5JSu2wWB18hbYfjpR55dvO5"
        access_token = "1143319962653560832-ggi4PS3OGStUcC5RLSPaV5YhwjJkE5"
        access_secret = "ZU48qIyslkpy6qVDRocKcXBDA7uS3ox7anwbtC5WJZHb7"
    except KeyError:
        sys.stderr.write("TWITTER_* environment variable not set\n")
        sys.exit(1)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return auth

# Creates connection to the twitter API
def get_twitter_client():
    auth = twitter_auth()
    client = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return client

# Checks if an input string contains numbers
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def fetchFeedTweets(screen_name):
    s = ""
    stop_words = set(stopwords.words('english'))
    # Downloads dictionary of English words
    nltk.download('words')
    words = set(nltk.corpus.words.words())

    #Establishes connection to Tweepy and the Twitter API
    auth = twitter_auth()
    client = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    # Get's the last 50 tweets in your feed... this would be from people you follow and what
    # they tweet or retweet
    for status in tweepy.Cursor(client.home_timeline, screen_name=screen_name).items(100):
        s += status.text

    #Clears any non english words or letters from the output string
    s = " ".join(w for w in nltk.wordpunct_tokenize(s) if w.lower() in words or not w.isalpha())

    # Parsing the string in terms of punctuation and capitalization
    table = str.maketrans('', '', string.punctuation)
    s = re.split(r'\W+', s)
    stripped = [w.translate(table) for w in s]
    words = [word.lower() for word in stripped]
    feedData = open("outputFile.txt", "w")
    for word in words:
        # Deletes any strings with numbers in them
        if not hasNumbers(word):
            if word not in stop_words and word != "get":
                feedData.writelines("(tweet)"+word+"\n")

def fetchNews():
    # Init
    newsapi = NewsApiClient(api_key='80979f75db4c46198e1fb95d6238d0b1')

    query = "Phoenix"

    all_articles = newsapi.get_everything(q=query,
                                          from_param='2020-07-15',
                                          to='2017-07-16',
                                          language='en',
                                          sort_by='relevancy')
    js = json.dumps(all_articles)

    f = open("outputFile.txt", "a")
    stop_words = set(stopwords.words('english'))

    for val in json.loads(js)["articles"]:
        descrip = val["description"]
        table = str.maketrans('', '', string.punctuation)
        s = re.split(r'\W+', descrip)
        stripped = [w.translate(table) for w in s]
        words = [word.lower() for word in stripped]
        for word in words:
            if word not in stop_words:
                if word != "get":
                    if word != query.lower():
                        f.write("(news)"+word+"\n")

def getFriends(screen_name):
    friends = []
    max_retry_count = 0 # create a max retry count so we don't have an infinite loop

    api_key = "DSt3NyAqOGFEGyUWzLRYZcx1g"
    api_secret = "581Fs2Q0hDctuMISQ83EkNp8xwc5JSu2wWB18hbYfjpR55dvO5"

    r = requests.post('https://api.twitter.com/oauth2/token?grant_type=client_credentials', auth=(api_key,api_secret))
    access_token = r.json()["access_token"]
    headers = {'Authorization':'Bearer {token}'.format(token=access_token)}

    next_cursor = -1

    while(next_cursor != 0):
        r = requests.get('https://api.twitter.com/1.1/friends/list.json?cursor={cursor}&screen_name={screen_name}&include_user_entities=true&skip_status=true&count=200'.format(cursor=next_cursor, screen_name=screen_name), headers=headers)

        if (r.status_code == 200):
            data = r.json()
            data_friends = [{ "id_str": user["id_str"], "screen_name":user["screen_name"], "friends_count":user["friends_count"]} for user in data["users"]]
            friends.extend(data_friends)

            next_cursor = data["next_cursor"]
            max_retry_count = 0
        elif (r.status_code == 401):
            next_cursor = 0
        else:
            max_retry_count = max_retry_count + 1
            print(r.status_code)
            print(max_retry_count)
            if (max_retry_count >= 20):
                raise Exception('max_retry_count limit reached')
            time.sleep(60)

    infoList = list()
    # Establishes connection to tweepy
    auth = twitter_auth()
    client = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    for friend in friends:
        id_str = friend["id_str"]
        a = client.get_user(id_str).name.encode('ascii', "ignore").decode()
        infoList.append(["(name)" + a + "\n"])

    followerData = open("outputFile.txt", "a")
    for row in infoList:
        for val in row:
            followerData.writelines(val)

    '''f = open("Allen_Lin_.dat")
    infoList = list()
    # Establishes connection to tweepy
    auth = twitter_auth()
    client = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    for x in f:
        info = x.split(",")
        # Parsing name and location
        a = client.get_user(str(info[0]).rstrip()).name.encode('ascii', "ignore").decode()
        location = info[10].rstrip().encode('ascii', "ignore").decode()
        # Appending their twitter ID, twitter name, and twitter location into a list
        infoList.append(["(name)" + a + "\n", "(location)" + location+"\n"])
    followerData = open("outputFile.txt", "a")
    for row in infoList:
        for val in row:
            followerData.writelines(val)'''

def convCelToFar(degrees):
    return degrees * 9 / 5 + 32;

def collectWeather(location):
    access_key = "12f055de782cfa6ac8cc58e120e297c2";
    url = "http://api.weatherstack.com/current?access_key=" + access_key + "&query=" + location
    response = requests.get(url)
    todos = json.loads(response.text)
    followerData = open("outputFile.txt", "a")
    followerData.writelines("(city)" + todos['location']['name'] + "\n")
    followerData.writelines("(state)" + todos['location']['region'] + "\n")
    temperature = convCelToFar(todos['current']['temperature'])
    temp_type = ""
    if temperature < 32:
        temp_type = 'freezing'
    elif temperature < 50:
        temp_type = 'cold'
    elif temperature < 70:
        temp_type = 'cool'
    elif temperature < 90:
        temp_type = "warm"
    else:
        temp_type = "hot"
    followerData.writelines("(temperature)" + temp_type + "\n")
    weather_descrptions = todos['current']['weather_descriptions']
    for w in weather_descrptions:
        followerData.writelines("(weather_desc)" + w + "\n")

location = input("Enter your city (ex. Chicago): ")
screen_name = input("Enter your Twitter handle (ex. VancityReynolds): ")

fetchFeedTweets(screen_name)
getFriends(screen_name)
fetchNews()
collectWeather(location)
