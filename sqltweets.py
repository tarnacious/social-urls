from sql import Tweet, session
import json

for row in session.query(Tweet).order_by(Tweet.id):
     tweet = json.loads(row.json)
     for url in tweet["entities"]["urls"]:
        print url["expanded_url"]
        print tweet["id"], tweet["text"]
