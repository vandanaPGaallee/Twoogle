from flask import Flask
import urllib.request, json, urllib
from flask import jsonify, request
from flask_cors import CORS
import ast
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
app = Flask(__name__)
CORS(app)
solr_url = "http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/solr/Twoogle/select?facet=on&indent=on&rows=20&sort=score%20desc&wt=json"
# vary = "facet.query=topic:%22infra%22&fq=topic:%22infra%22&q=*:*"
# temp = "http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/solr/Twoogle/select?json.facet={categories:{type:terms,field:hashtags}}&facet=on&indent=on&q=*:*&wt=json"
def ExtractDisplayContents(docs):
	# print(docs[0]["user.screen_name"][0])
	dict = []
	# print(docs[0])
	for doc in docs:
		# print(doc)
		temp = ast.literal_eval(doc["user"][0])
		# print(type(temp))
		# print("id", doc["id"])
		dict.append({"screen_name" : temp["screen_name"] if 'screen_name' in temp else "", "name" : temp["name"] if 'name' in temp else "", "link" : doc["id"] if 'id' in doc else "",  "summary" : doc["tweet_text"][0] if 'tweet_text' in doc else ""})
	return dict

def ModifyURL(req_data):
	global solr_url
	vary = ""
	for key, value in req_data.items(): 
		value = urllib.parse.quote(value)
		print(key,value)
		if key == "query":
			vary += "&q=*"+value+"*"
		elif(value != ""):
			vary += "&facet.query=" + key + ":" + value.lower()
			vary += "&fq=" + key + ":" + value.lower() if value != 'France' else value
	return solr_url + vary


@app.route("/getDefaultResults", methods=['POST', 'GET'])
def output():
	global solr_url
	mod_url = ""
	if request.method == 'POST':
		req_data = request.get_json()
		mod_url =ModifyURL(req_data)
		print(mod_url)
	# elif request.method == 'GET':
	# 	q = request.args.get('query') #if key doesn't exist, returns None
 #    	city = request.args['city'] #if key doesn't exist, returns a 400, bad request error
 #    	lang = request.args.get('lang')
 #    	topic = request.args.get('topic')
 #    	url = "" 
	with urllib.request.urlopen(mod_url) as url:
	    data = json.loads(url.read().decode())
	mod = jsonify(ExtractDisplayContents(data["response"]["docs"]))
	# print(ExtractDisplayContents(data["response"]["docs"]))
	return mod

@app.route("/data/<section>")
def data(section):
    assert section == request.view_args['section']
    with urllib.request.urlopen("http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/" + section + "/IRF18P1/select?facet.query=city:%22delhi%22&facet=on&indent=on&q=*:*&wt=json&rows=20") as url:
	    data = json.loads(url.read().decode())
	    print(type(data))
	    return  jsonify(data)

@app.route("/getPer/<field>")
def per(field):
	query = request.args.get('query')
	if query == None or query == '' or len(str(query)) == 0:
		query = ":"
	query = urllib.parse.quote(query)
	req_url = "http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/solr/Twoogle/select?json.facet={category:{type:terms,field:" + field + "}}&facet=on&indent=on&q=" + query +"&wt=json"
	with urllib.request.urlopen(req_url) as url:
		data = json.loads(url.read().decode())
	result = data["facets"]["category"]["buckets"]
	return jsonify(list(map(lambda x: {'value': x['count'], 'label': x['val']}, result)))

@app.route("/trending")
def trending():
  req_url = "http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/solr/Twoogle/select?json.facet={categories:{type:terms,field:hashtags}}&facet=on&indent=on&q=*:*&wt=json"
  with urllib.request.urlopen(req_url) as url:
    data = json.loads(url.read().decode())
    result = data["facets"]["categories"]["buckets"]
    return jsonify(list(map(lambda x: {'value': x['count'], 'label': x['val']}, result)))


def clean_tweet(tweet): 
	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", str(tweet)).split()) 

def get_tweet_sentiment(tweet): 

    analysis = TextBlob(clean_tweet(tweet)) 

    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

def get_tweets(jdata, count = 50): 
    tweets = [] 
    try: 
        for tweet in jdata: 
            parsed_tweet = {} 
            parsed_tweet['text'] = tweet['tweet_text'] 
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet['tweet_text'] ) 
            tweets.append(parsed_tweet)
        return tweets 
    except tweepy.TweepError as e: 
        print("Error : " + str(e)) 

@app.route("/sentiments")        
def sentiments():
	tweet=[]
	query = request.args.get('query')
	print(query)
	if query == None or query == '' or len(str(query)) == 0:
		query = "*:*"
	query = urllib.parse.quote(query)
	inurl = 'http://ec2-18-216-205-125.us-east-2.compute.amazonaws.com:8984/solr/Twoogle/select?facet=on&indent=on&q=' + query +'&wt=json'
	data = urllib.request.urlopen(inurl)
	docs= json.load(data)['response']['docs']
	for x in docs:
		if 'tweet_text' in x:
			tweet.append(x)
	print(len(tweet))        
	tweets = get_tweets(tweet, count = 50) 

	# picking positive tweets from tweets 
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
	# percentage of positive tweets 
	print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
	pp = 100*len(ptweets)/len(tweets)
	# picking negative tweets from tweets 
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
	# percentage of negative tweets 
	print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
	np = 100*len(ntweets)/len(tweets)
	# percentage of neutral tweets 
	print("Neutral tweets percentage: {} % ".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))) 
	nnp = 100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)
	# printing first 5 positive tweets 
	print("\n\nPositive tweets:") 
	for tweet in ptweets[:10]: 
		print(tweet['text']) 
	chart = [pp,np,nnp]
	print(chart)
	arr = [{"label": "Positive","value": chart[0]},{"label": "Negative","value": chart[1]},{"label": "Neutral","value": chart[2]}]
	print(arr)
	return jsonify(arr)


if __name__ == "__main__":
	app.run()


